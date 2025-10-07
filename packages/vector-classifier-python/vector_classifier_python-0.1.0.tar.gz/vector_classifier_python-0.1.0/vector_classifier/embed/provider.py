from __future__ import annotations
from typing import List, Protocol, Literal

class EmbeddingProvider(Protocol):
    @property
    def dimension(self) -> int: ...

    @property
    def modality(self) -> Literal["text", "image"]: ...

    async def embed_text_batch(self, texts: List[str]) -> List[List[float]]: ...

    async def embed_image_batch(self, image_urls: List[str]) -> List[List[float]]: ...

