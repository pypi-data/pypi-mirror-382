from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.corestructure.dataclass import DocumentUpload, VectorSearchResult, CollectionInfo

class BaseVectorStore(ABC):
    def __init__(self, **kwargs):
        self.config = kwargs
    
    @abstractmethod
    async def create_collection(self, name: str, embedding_model: str, metadata: Dict[str, Any] = None) -> bool:
        """Create a new collection"""
        pass
    
    @abstractmethod
    async def delete_collection(self, name: str) -> bool:
        """Delete a collection"""
        pass
    
    @abstractmethod
    async def add_documents(self, collection_name: str, dimension: int, documents: List[DocumentUpload]) -> bool:
        """Add documents to a collection"""
        pass
    
    @abstractmethod
    async def search_similar(self, collection_name: str, query_embedding: List[float], top_k: int = 5, similarity_threshold: float = 0.7) -> List[VectorSearchResult]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    async def get_collection_info(self, name: str) -> Optional[CollectionInfo]:
        """Get collection information"""
        pass
    
    @abstractmethod
    async def list_collections(self) -> List[CollectionInfo]:
        """List all collections"""
        pass
    
    @abstractmethod
    async def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        """Delete documents from a collection"""
        pass