"""This package contains utility functions for handling data from and to a MinIO cluster"""

import os
from minio import Minio, S3Error
from alidaparse.utils.progress import Progress
import logging
from tqdm import tqdm
import tempfile
import gdown
import requests


def sink(local_folder, bucket_name, minio_path, minio_url, access_key, secret_key):
    """
    Given a folder path or a file, this function will upload all the files to a path passed by minio_path
    :param local_folder:
    :param minio_url:
    :param bucket_name:
    :param minio_path:
    :param access_key:
    :param secret_key:
    :return:
    """
    minio_client = Minio(
        minio_url.replace("http://", "").replace("https://", ""),
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )
    # Check if the ALIDA's bucket exists
    if not minio_client.bucket_exists(bucket_name=bucket_name):
        raise RuntimeError(f"Cannot find the bucket {bucket_name}!")

    if os.path.isdir(local_folder):
        for root, _, files in os.walk(local_folder):
            for file in files:
                local_file_path = os.path.join(root, file)
                # Calculate the relative path to preserve folder structure
                relative_path = os.path.relpath(local_file_path, local_folder)
                # Compose the target path in MinIO
                object_name = os.path.join(minio_path, relative_path).replace("\\", "/")
                # for Windows compatibility
                try:
                    logging.warning(
                        f"Uploading to bucket {bucket_name}/{object_name} file {local_file_path}"
                    )
                    minio_client.fput_object(
                        bucket_name,
                        object_name,
                        local_file_path,
                        progress=Progress(),
                    )
                    logging.info(f"Uploaded: {object_name}")
                except S3Error as e:
                    logging.warning(f"Failed to upload {object_name}: {e}")
    else:
        # Compose the target path in MinIO
        object_name = os.path.join(minio_path, os.path.basename(local_folder)).replace(
            "\\", "/"
        )
        minio_client.fput_object(
            bucket_name,
            str(object_name),
            local_folder,
            progress=Progress(),
        )


def ls(
    remote_path,
    access_key,
    secret_key,
    bucket_name,
    minio_url,
    filter_by_extension: str | None = None,
    only_names: bool = False,
) -> list:

    if remote_path[-1] != "/":
        remote_path = remote_path + "/"

    cleaned = minio_url.replace("http://", "").replace("https://", "")
    client = Minio(cleaned, access_key=access_key, secret_key=secret_key, secure=False)
    objects = client.list_objects(bucket_name=bucket_name, prefix=remote_path)
    payload = []
    if filter_by_extension and only_names:
        filtered = filter(lambda o: o.name.endswith(filter_by_extension), objects)
        return [x.object_name for x in filtered]
    elif only_names:
        return [x.object_name for x in objects]
    elif filter_by_extension:
        for elem in objects:
            if elem.object_name.endswith(filter_by_extension):
                response = client.get_object(
                    bucket_name=bucket_name, object_name=elem.object_name
                )
                payload.append((elem.object_name, response))
                response.close()
                response.release_conn()
        return payload
    else:
        for elem in objects:
            response = client.get_object(
                bucket_name=bucket_name, object_name=elem.object_name
            )
            payload.append((elem.object_name, response))
            response.close()
            response.release_conn()
        return payload


def download_file(
    remote_path_to_object: str,
    minio_url,
    access_key,
    secret_key,
    bucket_name,
    to: str,
):
    cleaned = minio_url.replace("http://", "").replace("https://", "")
    client = Minio(cleaned, access_key=access_key, secret_key=secret_key, secure=False)
    # Get a full object
    response = client.get_object(bucket_name, remote_path_to_object)
    with tqdm(
        total=int(response.headers.get("content-length", 0)),
        unit="B",
        unit_scale=True,
    ) as progress_bar:
        with open(to, "wb") as file:
            for data in response.stream():
                progress_bar.update(len(data))
                file.write(data)


def download_google_drive_file_to_minio(
    google_id,
    filename,
    extension,
    remote_path_to_save,
    minio_url,
    minio_bucket,
    secret_key,
    access_key,
):
    with tempfile.TemporaryDirectory() as tmpdirname:
        gdown.download(
            output=f"{tmpdirname}/{filename}{extension}", id=google_id, quiet=False
        )
        sink(
            local_folder=f"{tmpdirname}",
            minio_url=minio_url,
            bucket_name=minio_bucket,
            minio_path=remote_path_to_save,
            secret_key=secret_key,
            access_key=access_key,
        )


def cURL_to_minio(
    url,
    filename,
    remote_minio_path_to_save,
    minio_url,
    minio_bucket,
    secret_key,
    access_key,
):
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Streaming, so we can iterate over the response.
        response = requests.get(url, stream=True)

        # Sizes in bytes.
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024

        with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
            with open(f"{tmpdirname}/{filename}", "wb") as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)

        if total_size != 0 and progress_bar.n != total_size:
            raise RuntimeError("Could not download file")
        sink(
            local_folder=f"{tmpdirname}",
            minio_url=minio_url,
            bucket_name=minio_bucket,
            minio_path=remote_minio_path_to_save,
            secret_key=secret_key,
            access_key=access_key,
        )
