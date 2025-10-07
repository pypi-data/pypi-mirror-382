# vector-classifier-python

Retrieval-based classification for structured data using embeddings and Pinecone. Zero-training, fast to integrate.

## Install

```bash
pip install vector-classifier-python pinecone openai huggingface_hub
```

## Quickstart

```python
from vector_classifier import VectorClassifier

classifier = VectorClassifier({
    "pinecone": {
        "api_key": "YOUR_PINECONE_API_KEY",
        "index_name": "animals",
        "metric": "cosine",
        "namespace": "prod"
    },
    "embedding": {
        "provider": "openai",
        "model": "text-embedding-3-small",
        "api_key": "YOUR_OPENAI_API_KEY"
    }
})

classifier.index_data([
    {"id": "1", "label": "Cat", "description": "Small domestic cat", "metadata": {"color": "gray"}},
    {"id": "2", "label": "Dog", "description": "Friendly domestic dog", "metadata": {"size": "medium"}},
])

result = classifier.classify({"description": "Playful feline"}, {"topK": 3, "threshold": 0.2})
print(result)
```

## API
- `index_data(records, options=None)`
- `classify(query, options=None)`
- `batch_classify(queries, options=None)`
- `update_entry(id, data, namespace=None)`
- `delete_index()`

See inline docs for details.

## Image embeddings and classification (CLIP + Pinecone)

Example mirroring the TypeScript `clip-plantnet.ts` is available at `examples/clip_plantnet.py`.

Environment variables required:

```bash
export HF_TOKEN=your_hf_token
export PINECONE_API_KEY=your_pinecone_key
export VC_INDEX=plantnet-clip
export VC_NAMESPACE=dev
export VC_MODEL=sentence-transformers/clip-ViT-B-32
```

Run the example:

```bash
python -m vector-classifier-python.examples.clip_plantnet
```

# vector-indexing-python

