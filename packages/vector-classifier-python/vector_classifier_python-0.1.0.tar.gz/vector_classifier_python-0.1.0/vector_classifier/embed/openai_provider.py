from __future__ import annotations
import asyncio
from typing import List
from openai import AsyncOpenAI

MODEL_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}

class OpenAIEmbeddingProvider:
    def __init__(self, *, api_key: str, model: str, base_url: str | None = None, embed_batch_size: int | None = None, concurrency: int | None = None) -> None:
        if not api_key:
            raise ValueError("OpenAI api_key is required")
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._dimension = MODEL_DIMENSIONS.get(model, 1536)
        self._batch_size = embed_batch_size or 256
        self._concurrency = concurrency or 4

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def modality(self) -> str:
        return "text"

    async def embed_text_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        chunks: list[list[str]] = [texts[i:i + self._batch_size] for i in range(0, len(texts), self._batch_size)]

        sem = asyncio.Semaphore(self._concurrency)

        async def run_chunk(chunk: list[str]) -> list[list[float]]:
            async with sem:
                res = await self._client.embeddings.create(model=self._model, input=chunk)
                return [d.embedding for d in res.data]

        results = await asyncio.gather(*[run_chunk(c) for c in chunks])
        return [*sum(results, [])]

    async def embed_image_batch(self, image_urls: List[str]) -> List[List[float]]:
        raise NotImplementedError("OpenAIEmbeddingProvider does not support image modality")

