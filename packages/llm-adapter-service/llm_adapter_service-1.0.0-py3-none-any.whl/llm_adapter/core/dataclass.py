from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from io import BytesIO

class FileTypeEnum(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    TXT = "txt"
    MD = "md"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    YAML = "yaml"

class VectorStoreEnum(str, Enum):
    CHROMA = "chroma"
    FAISS = "faiss"
    PINECONE = "pinecone"

class ProviderEnum(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

class EmbeddingModelEnum(str, Enum):
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_BASE = "text-embedding-3-base"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    LLAMA_TEXT_EMBED_V2 = "llama-text-embed-v2"
    EMBEDDING_GECKO = "embedding-gecko-001"
    EMBEDDING_001 = "embedding-001"
    TEXT_EMBEDDING_004 = "text-embedding-004"
    GEMINI_EMBEDDING_EXP_03_07 = "gemini-embedding-exp-03-07"
    GEMINI_EMBEDDING_EXP = "gemini-embedding-exp"


class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    GOOGLE = "google"

class SafetyLevel(Enum):
    SAFE = "safe"
    MODERATE = "moderate"
    HARMFUL = "harmful"

class llmdata(Enum):
    MAX_TOKENS = 4096
    DEFAULT_COST_PER_TOKEN = 0.000002
    CAPABILITIES = ["chat", "completion"]
    EMBEDDING_CAPABILITIES = ['embedding']

@dataclass
class ModelInfo:
    id: str
    name: str
    provider: ProviderType
    max_tokens: int
    cost_per_token: float
    capabilities: List[str]

@dataclass
class ChatRequest:
    prompt: str
    model_id: str
    user_id: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Conversation memory support
    conversation_messages: Optional[List[Dict[str, str]]] = None  # List of {"role": "user/assistant", "content": "..."}
    system_prompt: Optional[str] = None

@dataclass
class ChatResponse:
    response: str
    model_used: str
    tokens_used: int
    cost: float
    response_time: float
    safety_score: float
    timestamp: datetime
    accuracy_score: Optional[float] = None
    response_image: Optional[Union[BytesIO, str]] = None

@dataclass
class SafetyResult:
    is_safe: bool
    safety_level: SafetyLevel
    flagged_keywords: List[str]
    confidence_score: float
    reason: Optional[str] = None

@dataclass
class LogEntry:
    request_id: str
    user_id: str
    model_id: str
    input_prompt: str
    output_response: str
    tokens_used: int
    project_id: str
    session_id: str
    prompt_id: str
    prompt_type: str
    cost: float
    response_time: float
    safety_score: float
    accuracy_score: Optional[float]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class InsertEntrytoDB:
    request_id: str
    user_id: str
    model_id: str
    input_prompt: str
    output_response: str
    project_id: str
    session_id: str
    prompt_id: str
    prompt_type: str
    tokens_used: int
    cost: float
    response_time: float
    safety_score: float
    accuracy_score: Optional[float]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class EmbeddingRequest:
    text: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class EmbeddingResponse:
    embedding: List[float]
    model_used: str
    tokens_used: int
    cost: float
    response_time: float
    timestamp: datetime

@dataclass
class DocumentUpload:
    id: str
    content: Any
    metadata: Dict[str, Any]
    embedding: Optional[List[float]]
    createdattimestamp: datetime #Creation timestamp
    lastupdatedtimestamp: datetime #Last update timestamp

@dataclass
class RAGRequest:
    query: str
    model_id: str
    user_id: str
    collection_name: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_k: int = 5
    similarity_threshold: float = 0.7
    metadata: Optional[Dict[str, Any]] = None
    llm_api_key: Optional[str] = None

@dataclass
class RAGResponse:
    response: str
    model_used: str
    tokens_used: int
    cost: float
    response_time: float
    safety_score: float
    timestamp: datetime
    retrieved_documents: List[DocumentUpload]
    similarity_scores: List[float]
    context_used: str
    accuracy_score: Optional[float] = None

@dataclass
class VectorSearchResult:
    document: DocumentUpload
    similarity_score: float
    rank: int

@dataclass
class CollectionInfo:
    name: str
    document_count: int
    embedding_model: str
    createdattimestamp: datetime #Creation timestamp
    lastupdatedtimestamp: datetime #Last update timestamp
    metadata: Dict[str, Any]