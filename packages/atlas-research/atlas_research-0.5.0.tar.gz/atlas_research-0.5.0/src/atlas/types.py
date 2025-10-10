# 반드시 최상단에 추가해야 함
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional


class NodeType(str, Enum):
    PAPER = "Paper"
    CODEREPO = "CodeRepo"
    DATASET = "Dataset"
    CONCEPT = "Concept"
    AUTHOR = "Author"
    VENUE = "Venue"


class Author(BaseModel):
    name: str


class Paper(BaseModel):
    id: str = Field(..., description="External ID, e.g., arXiv ID")
    title: str
    summary: str
    authors: List[Author] = []
    published: Optional[str] = None
    url: Optional[str] = None
    categories: List[str] = []
