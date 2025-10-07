from __future__ import annotations
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..embed.openai_provider import OpenAIEmbeddingProvider
from ..embed.hf_provider import HFEmbeddingProvider
from ..vector.store import VectorStore, VectorUpsert
from ..vector.pinecone_store import PineconeVectorStore
from .registry import LocalRegistry


@dataclass
class RAGSource:
    url: str
    type: str  # "github" | "documentation" | "local"
    title: Optional[str] = None


class RAGClient:
    def __init__(
        self,
        *,
        pinecone_api_key: str,
        pinecone_index: str,
        pinecone_metric: str = "cosine",
        pinecone_cloud: Optional[str] = None,
        pinecone_region: Optional[str] = None,
        embedding_provider: str = "openai",
        embedding_model: str = "text-embedding-3-small",
        embedding_api_key: Optional[str] = None,
        embedding_base_url: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> None:
        if embedding_provider == "openai":
            self._embedder = OpenAIEmbeddingProvider(
                api_key=embedding_api_key or os.getenv("OPENAI_API_KEY", ""),
                model=embedding_model,
                base_url=embedding_base_url,
            )
        else:
            self._embedder = HFEmbeddingProvider(api_key=embedding_api_key, model=embedding_model)

        self._store: VectorStore = PineconeVectorStore(
            api_key=pinecone_api_key,
            index_name=pinecone_index or None,
            metric=pinecone_metric,  # type: ignore[arg-type]
            cloud=pinecone_cloud,
            region=pinecone_region,
        )
        self._namespace = namespace
        self._registry = LocalRegistry()

    async def ensure_index(self) -> None:
        await self._store.ensure_index(self._embedder.dimension, "cosine")  # type: ignore[arg-type]

    async def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, int]:
        texts = [str(c.get("content") or "") for c in chunks]
        vectors = await self._embedder.embed_text_batch(texts)  # type: ignore[attr-defined]
        upserts: List[VectorUpsert] = []
        chunk_ids: List[str] = []
        source_url: Optional[str] = None
        for i, c in enumerate(chunks):
            cid = str(c.get("id"))
            chunk_ids.append(cid)
            src = c.get("source", {}) or {}
            source_url = source_url or src.get("url")
            upserts.append(
                VectorUpsert(
                    id=cid,
                    values=[float(x) for x in vectors[i]],
                    metadata={
                        **(c.get("metadata") or {}),
                        "sourceUrl": src.get("url"),
                        "sourcePath": src.get("path"),
                        "sourceTitle": src.get("title"),
                        "content": str(c.get("content") or "")[:40000],
                    },
                )
            )
        res = await self._store.upsert(upserts, namespace=self._namespace)
        if source_url:
            self._registry.upsert_source(url=source_url, type="documentation", chunk_count=len(chunk_ids), status="indexed", chunk_ids=chunk_ids)
        return res

    async def query(self, *, query: str, top_k: int = 10, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        vector = (await self._embedder.embed_text_batch([query]))[0]  # type: ignore[attr-defined]
        matches = await self._store.query(vector, top_k, self._namespace, filter=filter, include_values=False)
        out: List[Dict[str, Any]] = []
        for m in matches:
            out.append({
                "id": m.id,
                "score": float(m.score),
                "metadata": m.metadata or {},
            })
        return out

    async def fetch_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        matches = await self._store.fetch(ids, namespace=self._namespace)
        return [{"id": m.id, "metadata": m.metadata or {}} for m in matches]

    def list_chunk_ids_for_url(self, url: str) -> List[str]:
        return self._registry.get_chunk_ids_by_url(url)


