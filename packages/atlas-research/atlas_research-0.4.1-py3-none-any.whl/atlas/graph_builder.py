from __future__ import annotations
import re
from typing import List, Tuple
import networkx as nx
from .types import Paper

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+-]{2,}")

def extract_keywords(text: str, top_k: int = 10) -> List[str]:
    tokens = WORD_RE.findall(text.lower())
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    scored = sorted(freq.items(), key=lambda x: (x[1], len(x[0])), reverse=True)
    return [w for w, _ in scored[:top_k]]

def build_graph(papers: List[Paper]) -> Tuple[nx.Graph, dict]:
    G = nx.Graph()
    meta = {"num_papers": len(papers)}
    for p in papers:
        pid = f"paper:{p.id}"
        G.add_node(pid, label=p.title, type="paper", url=p.url)
        for a in p.authors:
            aid = f"author:{a.name}"
            if not G.has_node(aid):
                G.add_node(aid, label=a.name, type="author")
            G.add_edge(pid, aid, weight=1.0, relation="authored_by")
        kws = extract_keywords((p.title or "") + "\n" + (p.summary or ""), top_k=8)
        for k in kws:
            kid = f"kw:{k}"
            if not G.has_node(kid):
                G.add_node(kid, label=k, type="keyword")
            if G.has_edge(pid, kid):
                G[pid][kid]["weight"] += 0.5
            else:
                G.add_edge(pid, kid, weight=0.5, relation="mentions")
    return G, meta
