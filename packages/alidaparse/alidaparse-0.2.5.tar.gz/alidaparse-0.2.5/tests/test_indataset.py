import pytest

from alidaparse.input import InDatasetFactory


def argv(n: int):
    payload = []
    for i in range(1, n + 1):
        payload.extend(
            [
                f"--input-dataset-{i}",
                f"dataset-{i}",
                f"--input-dataset-{i}.minio_bucket",
                f"minio-bucket-{i}",
                f"--input-dataset-{i}.minIO_URL",
                f"url-{i}",
                f"--input-dataset-{i}.minIO_ACCESS_KEY",
                f"access_key-{i}",
                f"--input-dataset-{i}.minIO_SECRET_KEY",
                f"secret_key-{i}",
            ]
        )

    return payload


def test_factory():
    d1, d2 = InDatasetFactory().from_cli(n=2, argv=argv(2))
    print(d1, d2)
