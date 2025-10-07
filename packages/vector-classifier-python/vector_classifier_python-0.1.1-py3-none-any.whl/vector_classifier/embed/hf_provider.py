from __future__ import annotations
import asyncio
import mimetypes
from typing import List, Optional
import requests
from huggingface_hub import InferenceClient

DEFAULT_DIMENSIONS = {
    "sentence-transformers/all-MiniLM-L6-v2": 384,
    "sentence-transformers/all-mpnet-base-v2": 768,
    "sentence-transformers/clip-ViT-B-32": 512,
    "openai/clip-vit-base-patch32": 512,
    "laion/CLIP-ViT-B-32-laion2B-s34B-b79K": 512,
    "google/vit-base-patch16-224": 1000,
}


def _infer_content_type(url: str) -> str:
    ctype, _ = mimetypes.guess_type(url)
    return ctype or "image/jpeg"


class HFEmbeddingProvider:
    def __init__(self, *, api_key: str, model: str, input_type: str | None = None, embed_batch_size: int | None = None, concurrency: int | None = None, endpoint_url: Optional[str] = None, direct: bool | None = None) -> None:
        if not api_key:
            raise ValueError("Hugging Face api_key is required")
        self._client = InferenceClient(token=api_key)
        self._token = api_key
        self._model = model
        self._modality = input_type or "text"
        self._dimension = DEFAULT_DIMENSIONS.get(model, 512)
        self._batch_size = embed_batch_size or 64
        self._concurrency = concurrency or 2
        self._endpoint_url = endpoint_url
        self._direct = bool(direct)

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def modality(self) -> str:
        return self._modality

    async def embed_text_batch(self, texts: List[str]) -> List[List[float]]:
        if self._modality != "text":
            raise RuntimeError("HF provider configured for image; cannot embed text")
        if not texts:
            return []
        chunks: list[list[str]] = [texts[i:i + self._batch_size] for i in range(0, len(texts), self._batch_size)]
        sem = asyncio.Semaphore(self._concurrency)

        async def run_chunk(chunk: list[str]) -> list[list[float]]:
            async with sem:
                if self._endpoint_url:
                    r = requests.post(self._endpoint_url, headers={"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}, json={"inputs": chunk})
                    r.raise_for_status()
                    return r.json()
                if self._direct:
                    r = requests.post(f"https://api-inference.huggingface.co/models/{self._model}", headers={"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}, json={"inputs": chunk})
                    r.raise_for_status()
                    return r.json()
                # official client (may be slower but simpler)
                return [self._client.feature_extraction(self._model, item) for item in chunk]  # type: ignore[return-value]

        results = await asyncio.gather(*[run_chunk(c) for c in chunks])
        flat: list[list[float]] = []
        for lst in results:
            for v in lst:
                flat.append(v)
        return flat

    async def embed_image_batch(self, image_urls: List[str]) -> List[List[float]]:
        if self._modality != "image":
            raise RuntimeError("HF provider configured for text; cannot embed image")
        if not image_urls:
            return []
        chunks: list[list[str]] = [image_urls[i:i + self._batch_size] for i in range(0, len(image_urls), self._batch_size)]
        sem = asyncio.Semaphore(self._concurrency)

        async def run_chunk(chunk: list[str]) -> list[list[float]]:
            outs: list[list[float]] = []
            async with sem:
                for url in chunk:
                    ctype = _infer_content_type(url)
                    data = requests.get(url, timeout=30).content
                    endpoint = self._endpoint_url or f"https://api-inference.huggingface.co/models/{self._model}"
                    r = requests.post(
                        endpoint,
                        headers={
                            "Authorization": f"Bearer {self._token}",
                            "Content-Type": ctype,
                        },
                        data=data,
                        timeout=60,
                    )
                    r.raise_for_status()
                    payload = r.json()
                    # If the model returns classification scores, map them to a fixed-size vector
                    if isinstance(payload, list) and payload and isinstance(payload[0], dict) and "score" in payload[0]:
                        vec = [0.0] * (DEFAULT_DIMENSIONS.get(self._model, 1000))
                        for item in payload:
                            label = str(item.get("label", ""))
                            score = float(item.get("score", 0.0))
                            idx = abs(hash(label)) % len(vec)
                            vec[idx] = score
                        outs.append(vec)
                    else:
                        outs.append([float(x) for x in payload])
            return outs

        results = await asyncio.gather(*[run_chunk(c) for c in chunks])
        flat: list[list[float]] = []
        for lst in results:
            for v in lst:
                flat.append(v)
        return flat

