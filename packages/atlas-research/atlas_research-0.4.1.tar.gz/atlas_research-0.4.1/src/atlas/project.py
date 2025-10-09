from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, Iterable
from .graph_store import GraphStore
from .ingest.basic import Ingestor
from .link.basic import Linker
from .query.api import QueryAPI
from .viz.pyvis_viz import Visualizer
from .export.report import Reporter
from .types import NodeType

class NodeType(str, Enum):
    PAPER = "Paper"
    CODEREPO = "CodeRepo"
    DATASET = "Dataset"
    CONCEPT = "Concept"
    AUTHOR = "Author"
    VENUE = "Venue"

@dataclass
class Atlas:
    name: str = "atlas-project"
    store: GraphStore = None

    def __post_init__(self):
        self.store = self.store or GraphStore()
        self.ingest = Ingestor(self.store)
        self.link = Linker(self.store)
        self.query = QueryAPI(self.store)
        self.viz = Visualizer(self.store)
        self.export = Reporter(self.store)

    # Convenience methods
    def add_node(self, ntype: NodeType, id: str, **attrs):
        return self.store.add_node(ntype, id, **attrs)

    def add_edge(self, src: str, dst: str, etype: str = "RELATES_TO", **attrs):
        return self.store.add_edge(src, dst, etype, **attrs)

    def save(self, path: str):
        self.store.save(path)

    def load(self, path: str):
        self.store.load(path)
