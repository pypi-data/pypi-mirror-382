from dataclasses import dataclass
from alidaparse.core import RemoteResource, RemoteResourceFactory


@dataclass
class InModel(RemoteResource):
    pass


class InModelFactory(RemoteResourceFactory):
    def __init__(self):
        super().__init__(InModel, "input-model")
