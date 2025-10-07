from __future__ import annotations
from typing import Any, Dict, List, Optional

from .client import RAGClient


async def search_documents(
    *,
    client: RAGClient,
    query: str,
    top_k: int = 10,
    sources: Optional[List[str]] = None,
    threshold: Optional[float] = None,
) -> Dict[str, Any]:
    flt: Dict[str, Any] = {}
    if sources:
        flt["sourceUrl"] = {"$in": sources}
    matches = await client.query(query=query, top_k=top_k, filter=flt or None)
    # Filter by threshold if provided
    if threshold is not None:
        matches = [m for m in matches if float(m.get("score", 0.0)) >= float(threshold)]
    # Enrich with chunk origin
    results: List[Dict[str, Any]] = []
    for m in matches:
        md = m.get("metadata", {})
        results.append({
            "id": m.get("id"),
            "score": m.get("score"),
            "chunk": {
                "id": m.get("id"),
                "sourceUrl": md.get("sourceUrl"),
                "sourcePath": md.get("sourcePath"),
                "sourceTitle": md.get("sourceTitle"),
            },
        })
    return {"success": True, "results": results, "totalResults": len(results)}


async def extract_content(
    *,
    client: RAGClient,
    url: str,
    chunk_id: Optional[str] = None,
    include_all_chunks: bool = False,
) -> Dict[str, Any]:
    if chunk_id:
        ids = [chunk_id]
    else:
        ids = []
        if include_all_chunks:
            ids = client.list_chunk_ids_for_url(url)
        if not ids:
            # Fallback: query meta-only by url to discover chunks
            matches = await client.query(query="*", top_k=50, filter={"sourceUrl": url})
            ids = [m["id"] for m in matches]
    docs = await client.fetch_by_ids(ids)
    out: List[Dict[str, Any]] = []
    for d in docs:
        md = d.get("metadata", {})
        out.append({
            "id": d.get("id"),
            "content": md.get("content"),
            "sourceUrl": md.get("sourceUrl"),
            "sourcePath": md.get("sourcePath"),
            "sourceTitle": md.get("sourceTitle"),
        })
    return {"success": True, "chunks": out}


