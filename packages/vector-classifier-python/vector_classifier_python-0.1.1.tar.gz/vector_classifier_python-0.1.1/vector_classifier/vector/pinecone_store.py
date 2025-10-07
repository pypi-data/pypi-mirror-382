from __future__ import annotations
from typing import Dict, List, Optional
from pinecone import Pinecone, ServerlessSpec
from ..utils.retry import with_retry
from .store import Metric, QueryMatch, VectorStore, VectorUpsert
import asyncio

class PineconeVectorStore(VectorStore):
    def __init__(self, *, api_key: str, index_name: Optional[str] = None, metric: Optional[Metric] = None, cloud: Optional[str] = None, region: Optional[str] = None) -> None:
        self._client = Pinecone(api_key=api_key)
        self._index_name = index_name or ""
        self._metric: Metric = metric or "cosine"
        self._cloud = cloud or "aws"
        self._region = region or "us-east-1"

    async def ensure_index(self, dimension: int, metric: Metric) -> None:
        self._metric = metric
        # Generate an index name if not provided
        if not self._index_name:
            self._index_name = f"vcp-{dimension}-{metric}".lower()
        existing = self._client.list_indexes()
        if any(i.name == self._index_name for i in (existing.indexes or [])):
            return
        self._client.create_index(
            name=self._index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud=self._cloud, region=self._region),
        )
        # wait until index is ready
        while True:
            d = self._client.describe_index(self._index_name)
            status = getattr(d, "status", None)
            ready = False
            if isinstance(status, dict):
                ready = bool(status.get("ready", False))
            else:
                ready = bool(getattr(status, "ready", False))
            if ready:
                break
            await asyncio.sleep(1.0)

    async def upsert(self, vectors: List[VectorUpsert], namespace: Optional[str] = None) -> Dict[str, int]:
        index = self._client.Index(self._index_name)
        async def _call() -> None:
            index.upsert(vectors=[{"id": v.id, "values": v.values, "metadata": v.metadata} for v in vectors], namespace=namespace or "")
        await with_retry(_call)
        return {"upsertedCount": len(vectors)}

    async def query(self, vector: List[float], top_k: int, namespace: Optional[str] = None, filter: Optional[Dict[str, object]] = None, include_values: bool = False) -> List[QueryMatch]:
        index = self._client.Index(self._index_name)
        async def _call():
            return index.query(top_k=top_k, vector=vector, include_metadata=True, include_values=include_values, namespace=namespace or "", filter=filter)
        res = await with_retry(_call)
        matches: List[QueryMatch] = []
        for m in getattr(res, "matches", []) or []:
            matches.append(QueryMatch(id=m.id, score=float(getattr(m, "score", 0.0) or 0.0), metadata=getattr(m, "metadata", None)))
        return matches

    async def fetch(self, ids: List[str], namespace: Optional[str] = None) -> List[QueryMatch]:
        index = self._client.Index(self._index_name)
        async def _call():
            return index.fetch(ids=ids, namespace=namespace or "")
        res = await with_retry(_call)
        vectors = getattr(res, "vectors", {}) or {}
        out: List[QueryMatch] = []
        for vid in ids:
            v = vectors.get(vid) if isinstance(vectors, dict) else None
            if v is None:
                continue
            meta = getattr(v, "metadata", None)
            out.append(QueryMatch(id=vid, score=1.0, metadata=meta))
        return out

    async def update(self, id: str, vector: List[float], metadata: Optional[Dict[str, object]] = None, namespace: Optional[str] = None) -> None:
        index = self._client.Index(self._index_name)
        index.upsert(vectors=[{"id": id, "values": vector, "metadata": metadata}], namespace=namespace or "")

    async def delete_index(self) -> None:
        self._client.delete_index(self._index_name)
