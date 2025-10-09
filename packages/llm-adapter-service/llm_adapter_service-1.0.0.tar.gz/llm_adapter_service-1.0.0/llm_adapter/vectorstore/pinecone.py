import pinecone
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.vectorstore.base import BaseVectorStore
from app.corestructure.dataclass import DocumentUpload, VectorSearchResult, CollectionInfo

class PineconeVectorStore(BaseVectorStore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.environment = kwargs.get('environment', 'us-east-1-aws')
        self.index_name_prefix = kwargs.get('index_name_prefix', 'llm_adapter')
        
        if not self.api_key:
            raise ValueError("Pinecone API key is required")    
        
        # Initialize Pinecone with new client
        self.client = pinecone.Pinecone(api_key=self.api_key)
        
        # Cache for active indexes
        self.active_indexes = {}
    
    def _get_index_name(self, collection_name: str) -> str:
        """Generate a standardized index name for Pinecone"""
        return f"{collection_name}"
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert metadata to Pinecone-compatible types"""
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
            index_name = f"{name}".lower()

            
            # Check if index already exists
            existing_indexes = self.client.list_indexes()
            if any(index.name == index_name for index in existing_indexes):
                return True
            
            # Sanitize metadata
            sanitized_metadata = self._sanitize_metadata(metadata or {})
            
            # Create Pinecone index using ServerlessSpec
            dimension = metadata.get("dimension", 1536)  # Default OpenAI embedding dimension
            
            # Create serverless index
            self.client.create_index(
                name=index_name,
                dimension=dimension,
                metric='cosine',
                spec=pinecone.ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            # Wait for index to be ready
            while True:
                index_description = self.client.describe_index(index_name)
                if index_description.status.ready:
                    break
                import time
                time.sleep(1)
            
            """  # Cache the index
            self.active_indexes[name] = self.client.Index(index_name)
            
            # Store collection metadata in the index
            collection_metadata = {
                "embedding_model": embedding_model,
                "created_at": datetime.now().isoformat(),
                "created_by": sanitized_metadata.get("created_by", "unknown"),
                "collection_name": name
            }
            
            # Add a metadata document to the index
            self.active_indexes[name].upsert(
                vectors=[{
                    "id": f"metadata_{name}",
                    "values": [0.0] * dimension,  # Dummy vector for metadata
                    "metadata": collection_metadata
                }]
            ) """
            
            return True
        except Exception as e:
            ##print(f"Error creating collection: {str(e)}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        try:
            index_name = self._get_index_name(name)
            
            existing_indexes = self.client.list_indexes()
            if index_name in [idx.name for idx in existing_indexes]:
                self.client.delete_index(index_name)
            
            if name in self.active_indexes:
                del self.active_indexes[name]
            
            return True
        except Exception as e:
            ##print(f"Error deleting collection: {str(e)}")
            return False
    
    async def add_documents(self, collection_name: str, dimension : int, documents: List[DocumentUpload]) -> bool:
        try:
            index_name = self._get_index_name(collection_name)
            
            # Check if collection exists and validate dimension
            if collection_name not in self.active_indexes:
                existing_indexes = self.client.list_indexes()
                if index_name in [idx.name for idx in existing_indexes]:
                    # Collection exists, check its expected dimension
                    index_description = self.client.describe_index(index_name)
                    expected_dimension = index_description.dimension
                    
                    if expected_dimension != dimension:
                        raise ValueError(f"Collection '{collection_name}' expects embeddings with dimension {expected_dimension}, but got {dimension}. The system will attempt to fix this automatically by resizing or recreating the embeddings.")
                    
                    self.active_indexes[collection_name] = self.client.Index(index_name)
                else:
                    # Collection doesn't exist, create it
                    await self.create_collection(
                        name=collection_name,
                        embedding_model="default",
                        metadata={"created_by": "system", "dimension": dimension}
                    )
                    self.active_indexes[collection_name] = self.client.Index(index_name)
            else:
                # Collection exists in cache, validate dimension
                index_description = self.client.describe_index(index_name)
                expected_dimension = index_description.dimension
                
                if expected_dimension != dimension:
                    raise ValueError(f"Collection '{collection_name}' expects embeddings with dimension {expected_dimension}, but got {dimension}. The system will attempt to fix this automatically by resizing or recreating the embeddings.")
            
            index = self.active_indexes[collection_name]
            
            # Filter documents with embeddings
            documents_with_embeddings = [doc for doc in documents if doc.embedding]
            
            if not documents_with_embeddings:
                return False
            
            # Prepare vectors for Pinecone
            vectors = []
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
                
                sanitized_metadata.update({
                    "content": text_content,
                    "created_at": doc.createdattimestamp.isoformat(),
                    "updated_at": doc.lastupdatedtimestamp.isoformat()
                })
                
                vectors.append({
                    "id": doc.id,
                    "values": doc.embedding,
                    "metadata": sanitized_metadata
                })
            
            # Upsert vectors in batches (Pinecone has limits)
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch)
            
            return True
        except Exception as e:
            ##print(f"Error adding documents: {str(e)}")
            return False
    
    def _get_or_create_index(self, collection_name: str) -> Optional[Any]:
        """Get or create index for collection"""
        index_name = self._get_index_name(collection_name)

        # Get index
        if collection_name not in self.active_indexes:

            existing_indexes = self.client.list_indexes()

            if index_name in [idx.name for idx in existing_indexes]:

                self.active_indexes[collection_name] = self.client.Index(index_name)
            else:

                return None
        
        return self.active_indexes[collection_name]

    def _parse_timestamp(self, timestamp_str: str, default: datetime = None) -> datetime:
        """Parse timestamp string with fallback to default"""
        if default is None:
            default = datetime.now()
        
        try:
            return datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            return default

    def _reconstruct_document_from_match(self, match: Any, rank: int) -> VectorSearchResult:
        """Reconstruct DocumentUpload from Pinecone match"""

        similarity_score = match.score

        
        # Reconstruct DocumentUpload from metadata
        metadata = match.metadata or {}
        content = metadata.get("content", "")
        
        # Parse timestamps
        created_at = self._parse_timestamp(metadata.get("created_at", datetime.now().isoformat()))
        updated_at = self._parse_timestamp(metadata.get("updated_at", datetime.now().isoformat()))
        
        # Remove content from metadata to avoid duplication
        doc_metadata = {k: v for k, v in metadata.items() if k not in ["content", "created_at", "updated_at"]}
        
        document = DocumentUpload(
            id=match.id,
            content=content,
            metadata=doc_metadata,
            embedding=None,  # We don't store embeddings in results
            createdattimestamp=created_at,
            lastupdatedtimestamp=updated_at
        )
        
        return VectorSearchResult(
            document=document,
            similarity_score=similarity_score,
            rank=rank
        )

    def _process_search_results(self, results: Any, similarity_threshold: float) -> List[VectorSearchResult]:
        """Process search results and filter by similarity threshold"""
        search_results = []
        for i, match in enumerate(results.matches):
            # Skip metadata documents
            if match.id.startswith("metadata_"):
                continue
            
            if match.score >= similarity_threshold:
                search_result = self._reconstruct_document_from_match(match, i + 1)
                search_results.append(search_result)
        
        return search_results

    async def search_similar(self, collection_name: str, query_embedding: List[float], top_k: int = 5, similarity_threshold: float = 0.7) -> List[VectorSearchResult]:
        try:
            # Get or create index
            index = self._get_or_create_index(collection_name)
            if index is None:
                return []
            
            
            # Search in Pinecone
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )

            
            # Process and filter results
            return self._process_search_results(results, similarity_threshold)
            
        except Exception as e:
            ##print(f"Error searching documents: {str(e)}")
            return []
    
    async def get_collection_info(self, name: str) -> Optional[CollectionInfo]:
        try:

            index_name = self._get_index_name(name)
            ###print("index_name: ", index_name)
            existing_indexes = self.client.list_indexes()
            ###print("existing_indexes: ", existing_indexes)
            if index_name not in [idx.name for idx in existing_indexes]:
                return None
 
            # Get index description
            index_description = self.client.describe_index(index_name)
            ###print("index_description: ", index_description)
            # Get index instance to query metadata
            if name not in self.active_indexes:
                self.active_indexes[name] = self.client.Index(index_name)
            ###print("active_indexes: ", self.active_indexes)
            index = self.active_indexes[name]
            ###print("index: ", index)
            # Query for metadata document
            metadata_results = index.query(
                vector=[0.0] * index_description.dimension,
                top_k=1,
                filter={"id": f"metadata_{name}"},
                include_metadata=True
            )
            ###print("metadata_results: ", metadata_results)
            metadata = {}
            created_at = datetime.now()
            
            if metadata_results.matches:
                metadata = metadata_results.matches[0].metadata or {}
                try:
                    created_at = datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat()))
                except (ValueError, TypeError):
                    created_at = datetime.now()
            ###print("metadata: ", metadata)
            # Get document count (approximate)
            # Note: Pinecone doesn't provide exact count, so we'll estimate
            stats = index.describe_index_stats()
            total_vector_count = stats.total_vector_count
            ###print("total_vector_count: ", total_vector_count)
            if total_vector_count == 0:
                total_vector_count = 1
            return CollectionInfo(
                name=name,
                document_count=total_vector_count - 1,  # Subtract metadata document
                embedding_model=metadata.get("embedding_model", "unknown"),
                createdattimestamp=created_at,
                lastupdatedtimestamp=datetime.now(),
                metadata=metadata
            )
        except Exception as e:
            ##print(f"Error getting collection info: {str(e)}")
            return None
    
    async def list_collections(self) -> List[CollectionInfo]:
        try:
            collections = []
            all_indexes = self.client.list_indexes()

            
            for index in all_indexes:
                # Extract collection name from index name
                #if index.name.startswith(self.index_name_prefix):
                #    collection_name = index.name[len(self.index_name_prefix) + 1:]  # Remove prefix and dash
                collection_name = index.name
                info = await self.get_collection_info(collection_name)
                if info:
                    collections.append(info)

            return collections
        except Exception as e:
            ##print(f"Error listing collections: {str(e)}")
            return []
    
    async def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        try:
            index_name = self._get_index_name(collection_name)
            
            existing_indexes = self.client.list_indexes()
            if index_name not in [idx.name for idx in existing_indexes]:
                ##print(f"Collection {collection_name} not found")
                return False
            
            # Get index
            if collection_name not in self.active_indexes:
                self.active_indexes[collection_name] = self.client.Index(index_name)
            
            index = self.active_indexes[collection_name]
            
            # Delete vectors by ID
            index.delete(ids=document_ids)
            
            return True
        except Exception as e:
            ##print(f"Error deleting documents: {str(e)}")
            return False
    
    async def get_collection_dimension(self, collection_name: str) -> Optional[int]:
        """Get the expected embedding dimension for a collection"""
        try:
            index_name = self._get_index_name(collection_name)
            
            existing_indexes = self.client.list_indexes()
            if index_name not in [idx.name for idx in existing_indexes]:
                return None
            
            # Get index description
            index_description = self.client.describe_index(index_name)
            return index_description.dimension
        except Exception as e:
            return None
    
    async def list_collections_with_dimensions(self) -> List[Dict[str, Any]]:
        """List all collections with their expected dimensions"""
        try:
            collection_info = []
            all_indexes = self.client.list_indexes()
            
            for index in all_indexes:
                collection_name = index.name
                
                # Get index description
                index_description = self.client.describe_index(collection_name)
                dimension = index_description.dimension
                
                # Get approximate document count
                try:
                    if collection_name not in self.active_indexes:
                        self.active_indexes[collection_name] = self.client.Index(collection_name)
                    
                    index_instance = self.active_indexes[collection_name]
                    stats = index_instance.describe_index_stats()
                    document_count = stats.total_vector_count
                except:
                    document_count = 0
                
                collection_info.append({
                    'name': collection_name,
                    'dimension': dimension,
                    'document_count': document_count,
                    'metadata': {
                        'index_name': collection_name,
                        'dimension': dimension
                    }
                })
            
            return collection_info
        except Exception as e:
            return [] 