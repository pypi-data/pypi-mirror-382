import argparse
from dataclasses import dataclass
import os
import uuid
from datetime import datetime
from kafka import KafkaProducer
import json
from typing import Literal, Union, Any, List, Dict

JSONSerializable = Union[
    None,
    bool,
    int,
    float,
    str,
    List["JSONSerializable"],
    Dict[str, "JSONSerializable"],
]


@dataclass(frozen=True)
class MessageBroker:
    go_manager_brokers: str
    go_manager_topic: str
    go_minio_path: str
    go_minio_bucket: str
    go_minio_url: str
    go_access_key: str
    go_secret_key: str
    go_use_ssl: bool

    def send_text(self, name, key, title, var, description):
        result = {
            "name": name,
            "key": key.lower().replace(" ", "-"),
            "uuid": str(uuid.uuid4()),
            "messageType": "text",
            "title": title,
            "description": description,
            "var": var,
            "created": str(datetime.now()),
            "modified": str(datetime.now()),
            "show": True,
        }
        self._send_message(result, self.go_manager_brokers, self.go_manager_topic)

    # def send_data(
    #     self,
    #     data_name,
    #     data_type: Union[Literal["metric"], Literal["picture"], Literal["text"]],
    #     extension: Union[Literal[".png"], Literal[".txt"], Literal[".jpg"]],
    #     local_data_path: str | None = None,
    #     data: JSONSerializable | None = None,
    #     **kwargs,
    # ):
    #     isFile = data_type == ".png" or data_type == ".jpg"
    #     if isFile and data_type != "picture":
    #         raise ValueError(
    #             f"You are trying to send an {extension} file that is not a picture"
    #         )
    #     if isFile and local_data_path is None:
    #         raise ValueError("No local data path provided")
    #
    #     if isFile:
    #         metadata = self._prepare_metadata(
    #             data_name,
    #             data_type,
    #             extension,
    #             local_path=local_data_path,
    #             go_minio_path=self.go_minio_path,
    #             **kwargs,
    #         )
    #         upload_file_to_minio(
    #             self.go_minio_url,
    #             self.go_access_key,
    #             self.go_secret_key,
    #             self.go_minio_bucket,
    #             self.go_minio_path + "/" + data_name,
    #             local_file_path=local_data_path,
    #             secure=self.go_use_ssl,
    #         )
    #     else:
    #         metadata = self._prepare_metadata(
    #             data_name,
    #             data_type,
    #             extension,
    #             data=data,
    #             **kwargs,
    #         )
    #     print(
    #         f"[MEDIA] {data_type}:{data_name}{extension} with filepath:{local_data_path} is being uploaded to minio"
    #     )
    #     self._send_message(metadata, self.go_manager_brokers, self.go_manager_topic)

    @staticmethod
    def _prepare_metadata(
        data_name: str,
        data_type: str,
        extension: str,
        local_path: str | None = None,
        go_minio_path: str | None = None,
        data: JSONSerializable = None,
        **kwargs,
    ):
        """
        This function prepares the necessary metadata that are needed for the ALIDA kafka-producer.
        :param data_name: The name of what is being sent
        :param data_type: The type of data being sent
        :param local_path: If what is sent is a picture, the path to it
        :param go_minio_path: The path to minio go (?)
        :param extension: The extension of what is being sent
        :param kwargs:
        :return:
        """
        metadata = MessageBroker._build_json(
            name=data_name, messageType=data_type, **kwargs
        )
        if local_path is not None:
            metadata["localPath"] = local_path
            metadata["path"] = go_minio_path + "/" + data_name
            metadata["filename"] = local_path
        else:
            metadata["filename"] = data
        metadata["extension"] = extension
        return metadata

    @staticmethod
    def _build_json(
        name: str, messageType: str, title=None, description=None, var=None, show=True
    ):
        """
        This function builds the JSON to associate with the media that is being sent
        :param name:
        :param messageType:
        :param title:
        :param description:
        :param var:
        :param show:
        :return:
        """
        result = {
            "name": name,
            "key": name.lower().replace(" ", "-"),
            "uuid": str(uuid.uuid4()),
            "messageType": messageType,
            "title": title,
            "description": description,
            "var": var,
            "created": str(datetime.now()),
            "modified": str(datetime.now()),
            "show": show,
        }
        if "BDA_ID" in os.environ:
            result["bdaId"] = os.environ.get("BDA_ID")

        if "SERVICE_ID" in os.environ:
            result["serviceId"] = os.environ.get("SERVICE_ID")

        if "ORGANIZATION_ID" in os.environ:
            result["organizationId"] = os.environ.get("ORGANIZATION_ID")

        if "OWNER_ID" in os.environ:
            result["ownerId"] = os.environ.get("OWNER_ID")

        if "EXECUTION_ID" in os.environ:
            result["executionId"] = os.environ.get("EXECUTION_ID")

        if "ACCESS_LEVEL" in os.environ:
            result["accessLevel"] = os.environ.get("ACCESS_LEVEL")

        if "EXECUTOR_ID" in os.environ:
            result["executorId"] = os.environ.get("EXECUTOR_ID")

        if "EXECUTOR_NAME" in os.environ:
            result["executorName"] = os.environ.get("EXECUTOR_NAME")

        if "EXECUTOR_ORG_ID" in os.environ:
            result["executorOrgId"] = os.environ.get("EXECUTOR_ORG_ID")

        if "EXECUTOR_ORG_NAME" in os.environ:
            result["executorOrgName"] = os.environ.get("EXECUTOR_ORG_NAME")
        return result

    @staticmethod
    def _send_message(data, go_manager_brokers, go_manager_topic):
        producer = KafkaProducer(bootstrap_servers=go_manager_brokers.split(","))
        producer.send(go_manager_topic, json.dumps(data).encode("utf-8"))
        producer.flush()


class MessageBrokerFactory:
    @staticmethod
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0", ""):
            return False

    @staticmethod
    def from_cli() -> "MessageBroker":
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "--go_manager.brokers", dest="go_manager_brokers", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.topic", dest="go_manager_topic", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.base_path", dest="go_minio_path", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.minio_bucket", dest="go_minio_bucket", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.minIO_URL", dest="go_minio_url", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.minIO_ACCESS_KEY",
            dest="go_access_key",
            type=str,
            required=True,
        )
        parser.add_argument(
            "--go_manager.minIO_SECRET_KEY",
            dest="go_secret_key",
            type=str,
            required=True,
        )
        parser.add_argument(
            "--go_manager.use_ssl",
            dest="go_use_ssl",
            type=MessageBrokerFactory.str2bool,
            required=True,
        )
        args, _ = parser.parse_known_args()
        return MessageBroker(
            go_manager_brokers=args.go_manager_brokers,
            go_manager_topic=args.go_manager_topic,
            go_minio_path=args.go_minio_path,
            go_minio_bucket=args.go_minio_bucket,
            go_minio_url=args.go_minio_url,
            go_access_key=args.go_access_key,
            go_secret_key=args.go_secret_key,
            go_use_ssl=args.go_use_ssl,
        )
