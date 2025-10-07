import argparse
from dataclasses import dataclass
from typing import Union, List, Sequence
from alidaparse.core import RemoteResource, RemoteResourceFactory


@dataclass
class InDataset(RemoteResource):
    pass


class InDatasetFactory(RemoteResourceFactory):
    def __init__(self):
        super().__init__(InDataset, "input-dataset")
