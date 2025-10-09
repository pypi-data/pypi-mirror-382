
from __future__ import annotations
from pathlib import Path
import datetime as _dt

class Reporter:
    def __init__(self, store):
        self.store = store

    def report(self, subgraph=None, path: str = "outputs/report.md", title: str = "Atlas Report"):
        G = subgraph or self.store.g
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# {title}", "", f"Generated: {_dt.datetime.now().isoformat(sep=' ', timespec='seconds')}", ""]
        lines.append("## Nodes")
        for nid, data in G.nodes(data=True):
            label = data.get("title") or data.get("name") or nid
            ntype = data.get("ntype", "")
            url = data.get("url", "")
            lines.append(f"- **{label}** ({ntype}) {url}")
        lines.append("")
        lines.append("## Edges")
        for u, v, key, data in G.edges(keys=True, data=True):
            et = data.get("etype", key)
            lines.append(f"- {u} --{et}--> {v}")
        Path(path).write_text("\n".join(lines), encoding="utf-8")
        return path
