import faiss
import numpy as np
import json
import os
import pickle
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.vectorstore.base import BaseVectorStore
from app.corestructure.dataclass import DocumentUpload, VectorSearchResult, CollectionInfo
from app.config import get_faiss_db_path

LITERAL_FILENAME = "collections_metadata.pkl"
class FaissVectorStore(BaseVectorStore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.persist_directory = kwargs.get('persist_directory', get_faiss_db_path())
        self.collections = {}
        self.collection_metadata = {}
        self.document_store = {}  # Store document content and metadata separately
        
        # Create persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Load existing collections
        self._load_collections()
    
    def _load_collections(self):
        """Load existing collections from disk"""
        try:
            metadata_file = os.path.join(self.persist_directory, LITERAL_FILENAME)
            if os.path.exists(metadata_file):
                with open(metadata_file, 'rb') as f:
                    self.collection_metadata = pickle.load(f)
            
            for collection_name in self.collection_metadata.keys():
                self._load_collection(collection_name)
        except Exception as e:
            ##print(f"Error loading collections: {str(e)}")
            pass
    
    def _load_collection(self, collection_name: str):
        """Load a specific collection from disk"""
        try:
            index_file = os.path.join(self.persist_directory, f'{collection_name}_index.faiss')
            docs_file = os.path.join(self.persist_directory, f'{collection_name}_docs.pkl')
            
            if os.path.exists(index_file):
                index = faiss.read_index(index_file)
                self.collections[collection_name] = index
                
                if os.path.exists(docs_file):
                    with open(docs_file, 'rb') as f:
                        self.document_store[collection_name] = pickle.load(f)
        except Exception as e:
            ##print(f"Error loading collection {collection_name}: {str(e)}")
            pass
    
    def _save_collection(self, collection_name: str):
        """Save a collection to disk"""
        try:
            if collection_name in self.collections:
                index_file = os.path.join(self.persist_directory, f'{collection_name}_index.faiss')
                docs_file = os.path.join(self.persist_directory, f'{collection_name}_docs.pkl')
                
                faiss.write_index(self.collections[collection_name], index_file)
                
                if collection_name in self.document_store:
                    with open(docs_file, 'wb') as f:
                        pickle.dump(self.document_store[collection_name], f)
                
                # Save metadata
                metadata_file = os.path.join(self.persist_directory, LITERAL_FILENAME)
                with open(metadata_file, 'wb') as f:
                    pickle.dump(self.collection_metadata, f)
        except Exception as e:
            ##print(f"Error saving collection {collection_name}: {str(e)}")
            pass
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert metadata to FAISS-compatible types"""
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
            
            # Sanitize metadata
            sanitized_metadata = self._sanitize_metadata(metadata or {})
            
            # Create FAISS index (using L2 distance by default)
            # Note: You might want to adjust the index type based on your needs
            dimension = metadata.get("dimension", 1536)  # Default OpenAI embedding dimension, adjust as needed
            index = faiss.IndexFlatL2(dimension)
            
            self.collections[name] = index
            self.document_store[name] = []
            self.collection_metadata[name] = {
                "embedding_model": embedding_model,
                "created_at": datetime.now().isoformat(),
                "created_by": sanitized_metadata.get("created_by", "unknown"),
                "dimension": dimension,
                "document_count": 0
            }
            
            self._save_collection(name)
            return True
        except Exception as e:
            ##print(f"Error creating collection: {str(e)}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        try:
            if name in self.collections:
                del self.collections[name]
            if name in self.document_store:
                del self.document_store[name]
            if name in self.collection_metadata:
                del self.collection_metadata[name]
            
            # Remove files
            index_file = os.path.join(self.persist_directory, f'{name}_index.faiss')
            docs_file = os.path.join(self.persist_directory, f'{name}_docs.pkl')
            
            if os.path.exists(index_file):
                os.remove(index_file)
            if os.path.exists(docs_file):
                os.remove(docs_file)
            
            # Save updated metadata
            metadata_file = os.path.join(self.persist_directory, LITERAL_FILENAME)
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.collection_metadata, f)
            
            return True
        except Exception as e:
            ##print(f"Error deleting collection: {str(e)}")
            return False
    
    async def add_documents(self, collection_name: str, dimension : int, documents: List[DocumentUpload]) -> bool:
        try:
            # Check if collection exists and validate dimension
            if collection_name not in self.collections:
                # Collection doesn't exist, create it
                await self.create_collection(
                    name=collection_name,
                    embedding_model="default",
                    metadata={"created_by": "system", "dimension": dimension}
                )
            else:
                # Collection exists, check its expected dimension
                collection_metadata = self.collection_metadata.get(collection_name, {})
                expected_dimension = collection_metadata.get('dimension', 1536)
                
                if expected_dimension != dimension:
                    raise ValueError(f"Collection '{collection_name}' expects embeddings with dimension {expected_dimension}, but got {dimension}. The system will attempt to fix this automatically by resizing or recreating the embeddings.")
            
            collection = self.collections[collection_name]
            documents_with_embeddings = [doc for doc in documents if doc.embedding]
            
            if not documents_with_embeddings:
                return False
            
            # Prepare embeddings for FAISS
            embeddings = np.array([doc.embedding for doc in documents_with_embeddings], dtype=np.float32)
            
            # Add to FAISS index
            collection.add(embeddings)
            
            # Store document content and metadata
            for doc in documents_with_embeddings:
                sanitized_metadata = self._sanitize_metadata(doc.metadata)
                
                # Extract text content from Document objects
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
                
                self.document_store[collection_name].append({
                    'id': doc.id,
                    'content': text_content,
                    'metadata': sanitized_metadata,
                    'created_at': doc.createdattimestamp.isoformat(),
                    'updated_at': doc.lastupdatedtimestamp.isoformat()
                })
            
            # Update metadata
            self.collection_metadata[collection_name]['document_count'] = len(self.document_store[collection_name])
            self.collection_metadata[collection_name]['last_updated'] = datetime.now().isoformat()
            
            self._save_collection(collection_name)
            return True
        except Exception as e:
            ##print(f"Error adding documents: {str(e)}")
            return False
    
    async def search_similar(self, collection_name: str, query_embedding: List[float], top_k: int = 5, similarity_threshold: float = 0.7) -> List[VectorSearchResult]:
        try:
            if collection_name not in self.collections:

                return []
            
            collection = self.collections[collection_name]
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search in FAISS
            distances, indices = collection.search(query_vector, top_k)
            
            search_results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.document_store[collection_name]):
                    # Convert distance to similarity score (L2 distance to cosine similarity approximation)
                    # Note: This is a rough conversion, you might want to use a different approach
                    similarity_score = 1.0 / (1.0 + distance)
                    
                    if similarity_score >= similarity_threshold:
                        doc_data = self.document_store[collection_name][idx]
                        
                        # Parse timestamps
                        try:
                            created_at = datetime.fromisoformat(doc_data['created_at'])
                            updated_at = datetime.fromisoformat(doc_data['updated_at'])
                        except (ValueError, TypeError):
                            created_at = updated_at = datetime.now()
                        
                        document = DocumentUpload(
                            id=doc_data['id'],
                            content=doc_data['content'],
                            metadata=doc_data['metadata'],
                            embedding=None,  # Don't return embeddings in search results
                            createdattimestamp=created_at,
                            lastupdatedtimestamp=updated_at
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
            if name not in self.collection_metadata:
                return None
            
            metadata = self.collection_metadata[name]
            document_count = metadata.get('document_count', 0)
            
            created_at_str = metadata.get('created_at', datetime.now().isoformat())
            try:
                created_at = datetime.fromisoformat(created_at_str)
            except (ValueError, TypeError):
                created_at = datetime.now()
            
            last_updated_str = metadata.get('last_updated', created_at_str)
            try:
                last_updated = datetime.fromisoformat(last_updated_str)
            except (ValueError, TypeError):
                last_updated = datetime.now()
            
            return CollectionInfo(
                name=name,
                document_count=document_count,
                embedding_model=metadata.get('embedding_model', 'unknown'),
                createdattimestamp=created_at,
                lastupdatedtimestamp=last_updated,
                metadata=metadata
            )
        except Exception as e:
            ##print(f"Error getting collection info: {str(e)}")
            return None
    
    async def list_collections(self) -> List[CollectionInfo]:
        try:
            collection_infos = []
            for collection_name in self.collection_metadata.keys():
                info = await self.get_collection_info(collection_name)
                if info:
                    collection_infos.append(info)
            
            return collection_infos
        except Exception as e:
            ##print(f"Error listing collections: {str(e)}")
            return []
    
    async def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        try:
            if collection_name not in self.collections:
                ##print(f"Collection {collection_name} not found")
                return False
            
            # FAISS doesn't support direct deletion, so we need to rebuild the index
            # This is a simplified implementation - in production you might want a more efficient approach
            
            # Get current documents excluding the ones to delete
            current_docs = self.document_store[collection_name]
            ids_to_delete = set(document_ids)
            
            # Filter out documents to delete
            remaining_docs = [doc for doc in current_docs if doc['id'] not in ids_to_delete]
            
            if len(remaining_docs) == 0:
                # If no documents left, delete the entire collection
                await self.delete_collection(collection_name)
                return True
            
            # Rebuild the index with remaining documents
            # Note: This requires the original embeddings, which we don't store
            # In a real implementation, you'd need to store embeddings separately or regenerate them
            
            ##print("Warning: FAISS deletion requires rebuilding index. This is not fully implemented.")
            return False
            
        except Exception as e:
            ##print(f"Error deleting documents: {str(e)}")
            return False
    
    async def get_collection_dimension(self, collection_name: str) -> Optional[int]:
        """Get the expected embedding dimension for a collection"""
        try:
            if collection_name not in self.collection_metadata:
                return None
            
            metadata = self.collection_metadata[collection_name]
            return metadata.get('dimension', 1536)
        except Exception as e:
            return None
    
    async def list_collections_with_dimensions(self) -> List[Dict[str, Any]]:
        """List all collections with their expected dimensions"""
        try:
            collection_info = []
            
            for collection_name, metadata in self.collection_metadata.items():
                dimension = metadata.get('dimension', 1536)
                document_count = metadata.get('document_count', 0)
                
                collection_info.append({
                    'name': collection_name,
                    'dimension': dimension,
                    'document_count': document_count,
                    'metadata': metadata
                })
            
            return collection_info
        except Exception as e:
            return []