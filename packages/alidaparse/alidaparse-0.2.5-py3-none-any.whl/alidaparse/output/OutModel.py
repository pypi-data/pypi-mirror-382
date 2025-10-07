from dataclasses import dataclass
from alidaparse.core import RemoteResource, RemoteResourceFactory


@dataclass
class OutModel(RemoteResource):
    pass


class OutModelFactory(RemoteResourceFactory):
    def __init__(self):
        super().__init__(OutModel, "output-model")
