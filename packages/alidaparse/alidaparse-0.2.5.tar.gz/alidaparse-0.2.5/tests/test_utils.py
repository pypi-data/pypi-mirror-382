"""This module test the minio utils functions"""

from alidaparse.utils import minio as minio_utils
from minio import Minio
import os
import pytest
import pickle

dir_path = os.path.dirname(os.path.realpath(__file__))
url = os.environ.get("MINIO_URL")
access_key = os.environ.get("MINIO_ACCESS_KEY")
secret_key = os.environ.get("MINIO_SECRET_KEY")
bucket = os.environ.get("MINIO_BUCKET")
path = os.environ.get("MINIO_PATH")


@pytest.fixture(scope="module")
def client():
    return Minio(url.replace("http://", ""), access_key, secret_key, secure=False)


def test_sink_single_file(client):
    minio_utils.sink(
        local_folder=os.path.join(dir_path, "test.txt"),
        minio_url=url,
        bucket_name=bucket,
        minio_path=path,
        access_key=access_key,
        secret_key=secret_key,
    )
    assert path + "/test.txt" in minio_utils.ls(
        remote_path=path,
        secret_key=secret_key,
        access_key=access_key,
        bucket_name=bucket,
        minio_url=url,
        only_names=True,
    )


def test_sink_multiple(client):
    local_folder = os.path.join(dir_path, "test_dir")
    minio_utils.sink(
        local_folder=local_folder,
        minio_url=url,
        bucket_name=bucket,
        minio_path=path,
        access_key=access_key,
        secret_key=secret_key,
    )
    for root, _, files in os.walk(local_folder):
        for file in files:
            assert path + "/" + file in minio_utils.ls(
                remote_path=path,
                secret_key=secret_key,
                access_key=access_key,
                bucket_name=bucket,
                minio_url=url,
                only_names=True,
            )


def test_sink_pkl_file(client):
    pkl_path = os.path.join(dir_path, "test_pkl.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump({"hello": "test"}, f)
    minio_utils.sink(
        local_folder=os.path.join(dir_path, "test_pkl.pkl"),
        minio_url=url,
        bucket_name=bucket,
        minio_path=path,
        access_key=access_key,
        secret_key=secret_key,
    )
    assert path + "/test_pkl.pkl" in minio_utils.ls(
        remote_path=path,
        secret_key=secret_key,
        access_key=access_key,
        bucket_name=bucket,
        minio_url=url,
        only_names=True,
    )
