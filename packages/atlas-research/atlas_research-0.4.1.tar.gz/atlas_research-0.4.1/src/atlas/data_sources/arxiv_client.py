from __future__ import annotations
from typing import List
import arxiv
from ..types import Paper, Author
from ..cache import get, set

def search_arxiv(query: str, max_results: int = 50) -> List[Paper]:
    cache_key = f"arxiv::{query}::{max_results}"
    cached = get(cache_key)
    if cached:
        return [Paper(**p) for p in cached]

    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    results: List[Paper] = []
    for r in search.results():
        authors = [Author(name=a.name) for a in r.authors]
        paper = Paper(
            id=r.get_short_id(),
            title=r.title,
            summary=r.summary,
            authors=authors,
            published=r.published.strftime("%Y-%m-%d") if r.published else None,
            url=r.entry_id,
            categories=list(r.categories or []),
        )
        results.append(paper)

    set(cache_key, [p.model_dump() for p in results])
    return results
