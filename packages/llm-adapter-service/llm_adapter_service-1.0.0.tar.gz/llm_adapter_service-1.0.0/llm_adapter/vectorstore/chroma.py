import chromadb
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.vectorstore.base import BaseVectorStore
from app.corestructure.dataclass import DocumentUpload, VectorSearchResult, CollectionInfo
from app.config import get_chroma_db_path

class ChromaVectorStore(BaseVectorStore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.persist_directory = kwargs.get('persist_directory', get_chroma_db_path())
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collections = {}
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert metadata to ChromaDB-compatible types"""
        sanitized = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, datetime):
                
                sanitized[key] = value.isoformat()
            elif isinstance(value, dict):
                sanitized[key] = json.dumps(value)
            elif value is None:
                sanitized[key] = ""
            else:
                sanitized[key] = str(value)
        return sanitized
    
    async def create_collection(self, name: str, embedding_model: str, metadata: Dict[str, Any] = None) -> bool:
        try:
            if name in self.collections:
                return True  # Collection already exists
            
            # Sanitize metadata for ChromaDB
            sanitized_metadata = self._sanitize_metadata(metadata or {})
            
            collection = self.client.create_collection(
                name=name,
                metadata={
                    "embedding_model": embedding_model,
                    "created_at": datetime.now().isoformat(),
                    "created_by": sanitized_metadata.get("created_by", "unknown"),
                    "dimension" : sanitized_metadata.get("dimension", 1536)
                }
            )
            self.collections[name] = collection
            return True
        except Exception as e:
            ##print(f"Error creating collection: {str(e)}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        try:
            self.client.delete_collection(name=name)
            if name in self.collections:
                del self.collections[name]
            return True
        except Exception as e:
            ##print(f"Error deleting collection: {str(e)}")
            return False
    
    async def add_documents(self, collection_name: str, dimension : int, documents: List[DocumentUpload]) -> bool:
        try:
            #print("collection_name-->", collection_name)
            #print("dimension-->", dimension)
            #print("documents-->", documents)
            
            # Check if collection exists and validate dimension
            if collection_name not in self.collections:
                try:
                    collection = self.client.get_collection(name=collection_name)
                    # Collection exists, check its expected dimension
                    collection_metadata = collection.metadata or {}
                    expected_dimension = collection_metadata.get('dimension', 1536)
                    
                    if expected_dimension != dimension:
                        raise ValueError(f"Collection '{collection_name}' expects embeddings with dimension {expected_dimension}, but got {dimension}. The system will attempt to fix this automatically by resizing or recreating the embeddings.")
                    
                    self.collections[collection_name] = collection
                except Exception as e:
                    # Collection doesn't exist, create it
                    await self.create_collection(
                        name=collection_name,
                        embedding_model="default",
                        metadata={"created_by": "system", "dimension": dimension},
                    )
                    collection = self.client.get_collection(name=collection_name)
                    self.collections[collection_name] = collection
            else:
                collection = self.collections[collection_name]
                
                # Validate dimension for existing collection
                collection_metadata = collection.metadata or {}
                expected_dimension = collection_metadata.get('dimension', 1536)
                
                if expected_dimension != dimension:
                    raise ValueError(f"Collection '{collection_name}' expects embeddings with dimension {expected_dimension}, but got {dimension}. The system will attempt to fix this automatically by resizing or recreating the embeddings.")
            
            #print("collection->add_documents", collection)

            ids = [doc.id for doc in documents]
            #print("ids-->", ids)
            # Extract text content from Document objects
            texts = []
            for doc in documents:
                text_content = doc.content
                if hasattr(doc.content, 'page_content'):
                    # If it's a Document object, extract the page_content
                    text_content = doc.content.page_content
                elif hasattr(doc.content, 'content'):
                    # If it's a Document object with content attribute
                    text_content = doc.content.content
                elif isinstance(doc.content, str):
                    # If it's already a string, use it as is
                    text_content = doc.content
                else:
                    # Convert to string if it's some other object
                    text_content = str(doc.content)
                texts.append(text_content)
            
            # Sanitize metadata for each document
            metadatas = [self._sanitize_metadata(doc.metadata) for doc in documents]
            #print("metadatas-->", metadatas)
            embeddings = [doc.embedding for doc in documents if doc.embedding]

            if embeddings:
                #print("embeddings-->", embeddings)

                collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
            else:

                collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
            
            #print("collection-->", collection)
            
            return True
        except Exception as e:
            #print(f"Error adding documents: {str(e)}")
            return False
    
    async def search_similar(self, collection_name: str, query_embedding: List[float], top_k: int = 5, similarity_threshold: float = 0.7) -> List[VectorSearchResult]:
        try:
            if collection_name not in self.collections:
                collection = self.client.get_collection(name=collection_name)
                self.collections[collection_name] = collection
            
            collection = self.collections[collection_name]
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            search_results = []
            for i, (doc_id, doc_text, metadata, distance) in enumerate(zip(
                results['ids'][0], 
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                similarity_score = 1 - distance  # Convert distance to similarity
                if similarity_score >= similarity_threshold:
                    document = DocumentUpload(
                        id=doc_id,
                        content=doc_text,
                        metadata=metadata or {},
                        embedding=None,
                        createdattimestamp=datetime.now(),
                        lastupdatedtimestamp=datetime.now()
                    )
                    search_results.append(VectorSearchResult(
                        document=document,
                        similarity_score=similarity_score,
                        rank=i + 1
                    ))
            
            return search_results
        except Exception as e:
            ##print(f"Error searching documents: {str(e)}")
            return []
    
    async def get_collection_info(self, name: str) -> Optional[CollectionInfo]:
        try:
            collection = self.client.get_collection(name=name)
            count = collection.count()
            metadata = collection.metadata or {}

            created_at_str = metadata.get('created_at', datetime.now().isoformat())
            try:
                created_at = datetime.fromisoformat(created_at_str)
            except (ValueError, TypeError):
                created_at = datetime.now()

            return CollectionInfo(
                name=name,
                document_count=count,
                embedding_model=metadata.get('embedding_model', 'unknown'),
                createdattimestamp=created_at,
                lastupdatedtimestamp=datetime.now(),
                metadata=metadata
            )
        except Exception as e:
            ##print(f"Error getting collection info: {str(e)}")
            return None
    
    async def list_collections(self) -> List[CollectionInfo]:
        try:
            collections = self.client.list_collections()
            collection_infos = []

            for collection in collections:

                info = await self.get_collection_info(collection.name)
                if info:
                    collection_infos.append(info)
            
            return collection_infos
        except Exception as e:

            ##print(f"Error listing collections: {str(e)}")
            return []
    
    async def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        try:
            if collection_name not in self.collections:
                collection = self.client.get_collection(name=collection_name)
                self.collections[collection_name] = collection
            
            collection = self.collections[collection_name]
            collection.delete(ids=document_ids)
            return True
        except Exception as e:
            ##print(f"Error deleting documents: {str(e)}")
            return False
    
    async def get_collection_dimension(self, collection_name: str) -> Optional[int]:
        """Get the expected embedding dimension for a collection"""
        try:
            if collection_name not in self.collections:
                collection = self.client.get_collection(name=collection_name)
                self.collections[collection_name] = collection
            
            collection = self.collections[collection_name]
            metadata = collection.metadata or {}
            return metadata.get('dimension', 1536)
        except Exception as e:
            return None
    
    async def list_collections_with_dimensions(self) -> List[Dict[str, Any]]:
        """List all collections with their expected dimensions"""
        try:
            collections = self.client.list_collections()
            collection_info = []
            
            for collection in collections:
                metadata = collection.metadata or {}
                dimension = metadata.get('dimension', 1536)
                count = collection.count()
                
                collection_info.append({
                    'name': collection.name,
                    'dimension': dimension,
                    'document_count': count,
                    'metadata': metadata
                })
            
            return collection_info
        except Exception as e:
            return []