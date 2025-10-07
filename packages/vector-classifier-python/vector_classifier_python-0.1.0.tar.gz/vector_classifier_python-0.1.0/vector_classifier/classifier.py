from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional, Tuple

from .preprocess.text import normalize_text
from .types import ClassifyOptions, ClassifyResult, ClassifierConfig, IndexDataOptions, QueryObject, StructuredRecord
from .utils.logger import create_logger
from .embed.openai_provider import OpenAIEmbeddingProvider
from .embed.hf_provider import HFEmbeddingProvider
from .vector.pinecone_store import PineconeVectorStore
from .vector.store import VectorStore, VectorUpsert
from .utils.vote import vote_label

class VectorClassifier:
    def __init__(self, config: ClassifierConfig) -> None:
        defaults = (config.get("defaults") or {})
        self._defaults = {
            "topK": defaults.get("topK", 5),
            "threshold": defaults.get("threshold", 0.0),
            "vote": defaults.get("vote", "weighted"),
        }
        self._logger = create_logger(config.get("logger"))

        emb = config["embedding"]
        provider = emb.get("provider")
        if provider == "custom":
            raise NotImplementedError("Custom embedding provider not implemented in Python version")
        elif provider == "openai":
            self._embedder = OpenAIEmbeddingProvider(api_key=emb.get("apiKey", ""), model=emb.get("model", "text-embedding-3-small"), base_url=emb.get("baseURL"), embed_batch_size=emb.get("embedBatchSize"), concurrency=emb.get("concurrency"))
        else:
            self._embedder = HFEmbeddingProvider(api_key=emb.get("apiKey", ""), model=emb.get("model", "sentence-transformers/all-MiniLM-L6-v2"), input_type=emb.get("inputType"), embed_batch_size=emb.get("embedBatchSize"), concurrency=emb.get("concurrency"))

        pine = config["pinecone"]
        self._namespace = pine.get("namespace")
        self._metric = pine.get("metric", "cosine")
        self._store: VectorStore = PineconeVectorStore(api_key=pine.get("apiKey", ""), index_name=pine.get("indexName"), metric=self._metric, cloud=pine.get("cloud"), region=pine.get("region"))

        pre = config.get("preprocess") or {}
        self._pre_record = pre.get("record")
        self._pre_query = pre.get("query")
        self._pre_text = pre.get("text")

    def _record_to_text(self, r: StructuredRecord) -> str:
        parts: list[str] = []
        if r.get("description"):
            parts.append(str(r["description"]))
        if r.get("label"):
            parts.append(f"label: {r['label']}")
        if r.get("metadata"):
            parts.append(f"metadata: {r['metadata']}")
        s = " | ".join(parts)
        return normalize_text(s)

    def _query_to_text(self, q: QueryObject) -> str:
        parts: list[str] = []
        if q.get("description"):
            parts.append(str(q["description"]))
        if q.get("metadata"):
            parts.append(f"metadata: {q['metadata']}")
        s = " | ".join(parts)
        return normalize_text(s)

    async def index_data(self, records: List[StructuredRecord], options: Optional[IndexDataOptions] = None) -> Dict[str, int]:
        opts = options or {}
        batch_size = int(opts.get("batchSize") or 256)
        namespace = opts.get("namespace") or self._namespace
        await self._store.ensure_index(self._embedder.dimension, self._metric)  # type: ignore[arg-type]

        recs = [self._pre_record(r) if callable(self._pre_record) else r for r in records]  # type: ignore[misc]
        texts = [self._record_to_text(r) for r in recs]
        processed_texts = [self._pre_text(t) if callable(self._pre_text) else t for t in texts]  # type: ignore[misc]

        # text or image modality
        vectors: List[List[float]]
        if getattr(self._embedder, "modality") == "text":
            vectors = await self._embedder.embed_text_batch(processed_texts)  # type: ignore[attr-defined]
        else:
            urls = [str(r.get("imageUrl") or "") for r in recs]
            vectors = await self._embedder.embed_image_batch(urls)  # type: ignore[attr-defined]

        to_upsert: List[VectorUpsert] = []
        for i, r in enumerate(recs):
            meta = dict(r.get("metadata") or {})
            if r.get("label") is not None:
                meta["label"] = r.get("label")
            if r.get("description") is not None:
                meta["description"] = r.get("description")
            to_upsert.append(VectorUpsert(id=r["id"], values=[float(x) for x in vectors[i]], metadata=meta))

        upserted = 0
        for i in range(0, len(to_upsert), batch_size):
            batch = to_upsert[i:i + batch_size]
            res = await self._store.upsert(batch, namespace)
            upserted += int(res.get("upsertedCount", 0))
        return {"upsertedCount": upserted}

    async def classify(self, query: QueryObject, options: Optional[ClassifyOptions] = None) -> ClassifyResult:
        opts = options or {}
        top_k = int(opts.get("topK") or self._defaults["topK"])  # type: ignore[index]
        threshold = float(opts.get("threshold") if opts.get("threshold") is not None else self._defaults["threshold"])  # type: ignore[index]
        namespace = opts.get("namespace") or self._namespace
        vote_mode = opts.get("vote") or self._defaults["vote"]  # type: ignore[index]

        await self._store.ensure_index(self._embedder.dimension, self._metric)  # type: ignore[arg-type]
        q = self._pre_query(query) if callable(self._pre_query) else query  # type: ignore[misc]
        qtext = self._pre_text(self._query_to_text(q)) if callable(self._pre_text) else self._query_to_text(q)  # type: ignore[misc]

        if getattr(self._embedder, "modality") == "text":
            vector = (await self._embedder.embed_text_batch([qtext]))[0]  # type: ignore[attr-defined]
        else:
            url = str(q.get("imageUrl") or "")
            vector = (await self._embedder.embed_image_batch([url]))[0]  # type: ignore[attr-defined]

        matches = await self._store.query(vector, top_k, namespace)

        def to_similarity(score: float) -> float:
            if self._metric == "euclidean":
                return 1.0 / (1.0 + max(0.0, score))
            return score

        with_sim = [
            {
                "id": m.id,
                "similarity": to_similarity(float(m.score or 0.0)),
                "metadata": m.metadata,
                "label": (m.metadata or {}).get("label") if m.metadata else None,
            }
            for m in matches
        ]
        top_list = [m for m in with_sim if m["similarity"] >= threshold]
        voted_label, _ = vote_label([(m.get("label"), float(m["similarity"])) for m in top_list], vote_mode)  # type: ignore[arg-type]
        confidence = float(top_list[0]["similarity"]) if top_list else None
        return {"predicted_label": voted_label, "confidence": confidence, "top_k": top_list}

    async def batch_classify(self, queries: List[QueryObject], options: Optional[ClassifyOptions] = None) -> List[ClassifyResult]:
        results: list[ClassifyResult] = []
        for q in queries:
            results.append(await self.classify(q, options))
        return results

    async def update_entry(self, id: str, data: Dict[str, Any], namespace: Optional[str] = None) -> None:
        rr: StructuredRecord = {"id": id, **data}
        rr = self._pre_record(rr) if callable(self._pre_record) else rr  # type: ignore[misc]
        text = self._record_to_text(rr)
        if getattr(self._embedder, "modality") == "text":
            vec = (await self._embedder.embed_text_batch([text]))[0]  # type: ignore[attr-defined]
        else:
            vec = (await self._embedder.embed_image_batch([str(rr.get("imageUrl") or "")]))[0]  # type: ignore[attr-defined]
        meta = dict(rr.get("metadata") or {})
        if rr.get("label") is not None:
            meta["label"] = rr.get("label")
        if rr.get("description") is not None:
            meta["description"] = rr.get("description")
        await self._store.update(id, [float(x) for x in vec], meta, namespace or self._namespace)

    async def delete_index(self) -> None:
        await self._store.delete_index()

