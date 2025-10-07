from dataclasses import dataclass
from alidaparse.core import RemoteResource, RemoteResourceFactory


@dataclass
class OutDataset(RemoteResource):
    pass


class OutDatasetFactory(RemoteResourceFactory):
    def __init__(self):
        super().__init__(OutDataset, "output-dataset")
