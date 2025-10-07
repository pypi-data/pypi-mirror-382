from dataclasses import dataclass
import argparse
from typing import Sequence


@dataclass
class RemoteResource:
    remote_path: str
    minio_bucket: str
    minio_url: str
    access_key: str
    secret_key: str


class RemoteResourceFactory:
    def __init__(self, cls, prefix: str):
        self.cls = cls
        self.prefix = prefix

    @staticmethod
    def register_remote_resource_args(
        parser: argparse.ArgumentParser, prefix: str, index: int | None = None
    ):
        """Register CLI arguments for a remote resource (safe dest names)."""
        safe_prefix = prefix.replace("-", "_")
        suffix = f"-{index}" if index else ""
        dest_prefix = f"{safe_prefix}_{index}" if index else safe_prefix

        parser.add_argument(
            f"--{prefix}{suffix}", dest=dest_prefix, type=str, required=True
        )
        parser.add_argument(
            f"--{prefix}{suffix}.minio_bucket",
            dest=f"{dest_prefix}_minio_bucket",
            type=str,
            required=True,
        )
        parser.add_argument(
            f"--{prefix}{suffix}.minIO_URL",
            dest=f"{dest_prefix}_minio_url",
            type=str,
            required=True,
        )
        parser.add_argument(
            f"--{prefix}{suffix}.minIO_ACCESS_KEY",
            dest=f"{dest_prefix}_access_key",
            type=str,
            required=True,
        )
        parser.add_argument(
            f"--{prefix}{suffix}.minIO_SECRET_KEY",
            dest=f"{dest_prefix}_secret_key",
            type=str,
            required=True,
        )

    def from_cli(self, n: int = 1, argv: Sequence[str] | None = None):
        """Parse CLI args into one or more RemoteResource-derived objects."""
        parser = argparse.ArgumentParser()
        objs = []

        # --- register arguments ---
        if n > 1:
            for i in range(1, n + 1):
                self.register_remote_resource_args(parser, self.prefix, i)
        else:
            self.register_remote_resource_args(parser, self.prefix)

        # --- parse arguments ---
        args, _ = parser.parse_known_args(argv)

        # --- build object(s) ---
        safe_prefix = self.prefix.replace("-", "_")
        dest_prefix_base = safe_prefix
        indices = range(1, n + 1) if n > 1 else [None]

        for i in indices:
            dest_prefix = f"{dest_prefix_base}_{i}" if i else dest_prefix_base
            objs.append(
                self.cls(
                    remote_path=getattr(args, dest_prefix),
                    minio_bucket=getattr(args, f"{dest_prefix}_minio_bucket"),
                    minio_url=getattr(args, f"{dest_prefix}_minio_url"),
                    access_key=getattr(args, f"{dest_prefix}_access_key"),
                    secret_key=getattr(args, f"{dest_prefix}_secret_key"),
                )
            )

        return objs if n > 1 else objs[0]
