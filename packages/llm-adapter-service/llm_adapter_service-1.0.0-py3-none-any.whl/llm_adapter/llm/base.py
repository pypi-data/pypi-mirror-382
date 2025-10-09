from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator
from app.corestructure.dataclass import ModelInfo, ChatRequest, ChatResponse, DocumentUpload, VectorSearchResult, CollectionInfo, EmbeddingRequest, EmbeddingResponse

class BaseLLMAdapter(ABC):
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """List available models from the provider"""
        pass
    
    @abstractmethod
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Execute chat completion"""
        pass
    
    @abstractmethod
    async def chat_completion_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Execute streaming chat completion"""
        pass
    
    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate connection to the provider"""
        pass
    
    @abstractmethod
    async def create_embedding(self, request: EmbeddingRequest, api_key: str) -> EmbeddingResponse:
        """Create embedding for the given text"""
        pass
    
    @abstractmethod
    async def create_embeddings_batch(self, requests: List[EmbeddingRequest], api_key: str) -> List[EmbeddingResponse]:
        """Create embeddings for multiple texts"""
        pass
    
    def get_provider_type(self) -> str:
        return self.__class__.__name__.replace('Adapter', '').lower()
    
    