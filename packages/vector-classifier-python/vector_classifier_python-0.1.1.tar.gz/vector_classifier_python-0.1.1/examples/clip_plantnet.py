import asyncio
import os
import random
from typing import Any, Dict, List, Optional, TypedDict

from vector_classifier import VectorClassifier

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


class PlantRow(TypedDict, total=False):
    id: str
    label: Optional[str]
    imageUrl: str


async def fetch_plantnet_sample(limit: int = 20) -> List[PlantRow]:
    import requests

    url = "https://datasets-server.huggingface.co/rows"
    params = {
        "dataset": "mikehemberger/plantnet300K",
        "config": "default",
        "split": "train",
        "offset": "0",
        "length": str(limit),
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data: Dict[str, Any] = r.json()
    features: List[Dict[str, Any]] = data.get("features") or []
    image_col = next((f for f in features if f.get("name") == "image"), None)
    label_col = next((f for f in features if f.get("name") == "label"), None)
    rows: List[Dict[str, Any]] = data.get("rows") or []
    out: List[PlantRow] = []
    for r in rows:
        row_obj: Dict[str, Any] = r.get("row") or {}
        img_cell = row_obj.get(image_col.get("name")) if image_col else None
        label_cell = row_obj.get(label_col.get("name")) if label_col else None
        src: Optional[str] = (
            (img_cell or {}).get("src")
            or (img_cell or {}).get("image", {}).get("src")
            or (img_cell or {}).get("url")
            or ((img_cell or {}).get("value") or {}).get("src")
        )
        label_val: Optional[str] = None
        if label_cell is not None:
            try:
                label_val = str(label_cell.get("value") if isinstance(label_cell, dict) else label_cell)
            except Exception:
                label_val = None
        if src:
            out.append({"id": str(r.get("row_idx", len(out))), "label": label_val, "imageUrl": src})
    return out


async def main() -> None:
    # Requires: HF_TOKEN, PINECONE_API_KEY
    hf_token = os.environ.get("HF_TOKEN")
    pine_api = os.environ.get("PINECONE_API_KEY")
    if not hf_token:
        raise RuntimeError("HF_TOKEN is required for Hugging Face inference")
    if not pine_api:
        raise RuntimeError("PINECONE_API_KEY is required for Pinecone")

    sample = await fetch_plantnet_sample(24)
    if not sample:
        raise RuntimeError("No sample rows found from plantnet300K")

    classifier = VectorClassifier({
        "pinecone": {
            "apiKey": pine_api,
            "indexName": os.environ.get("VC_INDEX", "plantnet-clip"),
            "metric": "cosine",
            "namespace": os.environ.get("VC_NAMESPACE", "dev"),
            "cloud": os.environ.get("VC_CLOUD", "aws"),
            "region": os.environ.get("VC_REGION", "us-east-1"),
        },
        "embedding": {
            "provider": "hf",
            "model": os.environ.get("VC_MODEL", "sentence-transformers/clip-ViT-B-32"),
            "apiKey": hf_token,
            "inputType": "image",
            "embedBatchSize": int(os.environ.get("VC_EMBED_BATCH", "8")),
            "concurrency": int(os.environ.get("VC_CONCURRENCY", "2")),
        },
        "preprocess": {
            # passthrough; could resize/normalize URLs here if needed
            "record": lambda r: r,
            "query": lambda q: q,
        },
    })

    # Index a small batch from the dataset
    await classifier.index_data([
        {"id": r["id"], "label": r.get("label"), "imageUrl": r["imageUrl"], "metadata": {"dataset": "plantnet300K"}}
        for r in sample
    ], {"batchSize": 16})

    # Give Pinecone a brief moment to index vectors
    await asyncio.sleep(2.0)

    # Classify using one image from the sample (simulates retrieval/classification)
    test = random.choice(sample)
    result = await classifier.classify({"imageUrl": test["imageUrl"]}, {"topK": 10, "threshold": 0})
    print({
        "query_label": test.get("label"),
        "predicted_label": result.get("predicted_label"),
        "top_k": result.get("top_k", [])[:3],
    })


if __name__ == "__main__":
    asyncio.run(main())


