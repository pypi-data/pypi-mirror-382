from typing import Optional
from ..types import NodeType


class Ingestor:
    def __init__(self, store):
        self.store = store

    def paper(self, id: str, title: Optional[str] = None, url: Optional[str] = None, year: Optional[int] = None, **meta):
        nid = self.store.add_node(NodeType.PAPER.value, id, title=title, url=url, year=year, **meta)
        return nid

    def repo(self, id: str, name: Optional[str] = None, url: Optional[str] = None, **meta):
        nid = self.store.add_node(NodeType.CODEREPO.value, id, name=name or id, url=url, **meta)
        return nid

    def dataset(self, id: str, name: Optional[str] = None, url: Optional[str] = None, **meta):
        nid = self.store.add_node(NodeType.DATASET.value, id, name=name or id, url=url, **meta)
        return nid

    def concept(self, id: str, **meta):
        return self.store.add_node(NodeType.CONCEPT.value, id, **meta)
