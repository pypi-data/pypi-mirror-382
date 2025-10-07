from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Protocol, TypedDict

Metric = Literal["cosine", "euclidean"]
LoggerKind = Literal["silent", "json", "pretty"]

class StructuredRecord(TypedDict, total=False):
    id: str
    label: Optional[str]
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    imageUrl: Optional[str]

class QueryObject(TypedDict, total=False):
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    imageUrl: Optional[str]

class ClassifyOptions(TypedDict, total=False):
    topK: Optional[int]
    threshold: Optional[float]
    namespace: Optional[str]
    vote: Optional[Literal["majority", "weighted"]]

class TopKMatch(TypedDict, total=False):
    id: str
    similarity: float
    metadata: Optional[Dict[str, Any]]
    label: Optional[str]

class ClassifyResult(TypedDict, total=False):
    predicted_label: Optional[str]
    confidence: Optional[float]
    top_k: List[TopKMatch]

class IndexDataOptions(TypedDict, total=False):
    batchSize: Optional[int]
    namespace: Optional[str]
    embedBatchSize: Optional[int]
    concurrency: Optional[int]

class EmbeddingModelConfig(TypedDict, total=False):
    provider: Literal["openai", "hf"]
    model: str
    apiKey: Optional[str]
    baseURL: Optional[str]
    concurrency: Optional[int]
    embedBatchSize: Optional[int]
    inputType: Optional[Literal["text", "image"]]

class CustomEmbeddingConfig(TypedDict, total=False):
    provider: Literal["custom"]
    embed: Any  # Callable[[List[str]], List[List[float]]]
    dimension: int

EmbeddingConfig = EmbeddingModelConfig | CustomEmbeddingConfig

class PineconeConfig(TypedDict, total=False):
    apiKey: str
    indexName: str
    metric: Optional[Metric]
    namespace: Optional[str]
    cloud: Optional[Literal["aws", "gcp", "azure"]]
    region: Optional[str]

class ClassifierDefaults(TypedDict, total=False):
    topK: Optional[int]
    threshold: Optional[float]
    vote: Optional[Literal["majority", "weighted"]]

class ClassifierConfig(TypedDict, total=False):
    pinecone: PineconeConfig
    embedding: EmbeddingConfig
    defaults: Optional[ClassifierDefaults]
    logger: Optional[LoggerKind]
    preprocess: Optional[Dict[str, Any]]

