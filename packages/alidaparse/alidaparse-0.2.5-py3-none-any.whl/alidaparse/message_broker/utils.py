from minio import Minio


def upload_file_to_minio(
    minio_url,
    access_key,
    secret_key,
    bucket_name,
    object_name,
    local_file_path,
    secure=False,
):
    # Initialize the MinIO client
    address = minio_url.replace("http://", "").replace("https://", "")
    client = Minio(address, access_key=access_key, secret_key=secret_key, secure=secure)
    print(f"{address, access_key, secret_key, secure}")
    # Upload the file
    client.fput_object(bucket_name, object_name, local_file_path)
    print(
        f"[UPLOAD] bucket={bucket_name} object={object_name} local={local_file_path} endpoint={address} secure={secure}"
    )
    print(bucket_name, object_name, local_file_path)
