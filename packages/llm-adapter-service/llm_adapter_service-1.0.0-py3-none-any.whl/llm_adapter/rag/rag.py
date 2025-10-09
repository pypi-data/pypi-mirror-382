import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.llm.base import BaseLLMAdapter
from fastapi import HTTPException
from app.vectorstore.base import BaseVectorStore
from app.corestructure.dataclass import RAGRequest, RAGResponse, DocumentUpload, VectorSearchResult, EmbeddingRequest, ChatRequest, ChatResponse, EmbeddingResponse

class RAGExecutor:
    def __init__(self, llm_adapter: BaseLLMAdapter, embedding_adapter: BaseLLMAdapter, vector_store: BaseVectorStore):
        self.llm_adapter = llm_adapter
        self.embedding_adapter = embedding_adapter
        self.vector_store = vector_store

    
    async def execute_rag(self, request: RAGRequest) -> RAGResponse:

        start_time = time.time()
        
        try:
            # Step 1: Create embedding for the query

            query_embedding_request = EmbeddingRequest(
                text=request.query,
                user_id=request.user_id,
                metadata=request.metadata
            )

            query_embedding_response = await self.embedding_adapter.create_embedding(query_embedding_request, api_key=request.llm_api_key)

            # Step 2: Search for similar documents

            search_results = await self.vector_store.search_similar(
                collection_name=request.collection_name,
                query_embedding=query_embedding_response.embedding,
                top_k=request.top_k,
                similarity_threshold=request.similarity_threshold
            )
            # Step 3: Prepare context from retrieved documents

            context = self._prepare_context(search_results)

            # Step 4: Create enhanced prompt with context
            enhanced_prompt = self._create_enhanced_prompt(request.query, context)

            # Step 5: Generate response using LLM
           
            chat_request = ChatRequest(
                prompt=enhanced_prompt,
                model_id=request.model_id,
                user_id=request.user_id,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                metadata=request.metadata
            )

            chat_response = await self.llm_adapter.chat_completion(chat_request)

            end_time = time.time()
            
            return RAGResponse(
                response=chat_response.response,
                model_used=chat_response.model_used,
                tokens_used=chat_response.tokens_used + query_embedding_response.tokens_used,
                cost=chat_response.cost + query_embedding_response.cost,
                response_time=end_time - start_time,
                safety_score=chat_response.safety_score,
                timestamp=datetime.now(),
                retrieved_documents=[result.document for result in search_results],
                similarity_scores=[result.similarity_score for result in search_results],
                context_used=context, 
                accuracy_score=chat_response.accuracy_score
            )
            
        except Exception as e:
            raise HTTPException(f"RAG execution error: {str(e)}")
    
    async def execute_rag_with_conversation(self, request: RAGRequest, conversation_messages: List[Dict[str, str]], 
                                          system_prompt: Optional[str] = None) -> RAGResponse:
        """Execute RAG query with conversation context"""
        start_time = time.time()
        
        try:
            # Step 1: Create embedding for the query

            query_embedding_request = EmbeddingRequest(
                text=request.query,
                user_id=request.user_id,
                metadata=request.metadata
            )
            query_embedding_response = await self.embedding_adapter.create_embedding(query_embedding_request, api_key=request.llm_api_key)
            
            # Step 2: Search for similar documents
            search_results = await self.vector_store.search_similar(
                collection_name=request.collection_name,
                query_embedding=query_embedding_response.embedding,
                top_k=request.top_k,
                similarity_threshold=request.similarity_threshold
            )
            
            # Step 3: Prepare context from retrieved documents
            context = self._prepare_context(search_results)
            
            # Step 4: Create enhanced prompt with context and conversation history
            enhanced_prompt = self._create_enhanced_prompt_with_conversation(
                request.query, context, conversation_messages, system_prompt
            )
            
            # Step 5: Generate response using LLM with conversation context
            chat_request = ChatRequest(
                prompt=enhanced_prompt,
                model_id=request.model_id,
                user_id=request.user_id,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                metadata=request.metadata,
                conversation_messages=conversation_messages,
                system_prompt=system_prompt
            )

            chat_response = await self.llm_adapter.chat_completion(chat_request)

            end_time = time.time()
            
            return RAGResponse(
                response=chat_response.response,
                model_used=chat_response.model_used,
                tokens_used=chat_response.tokens_used + query_embedding_response.tokens_used,
                cost=chat_response.cost + query_embedding_response.cost,
                response_time=end_time - start_time,
                safety_score=chat_response.safety_score,
                timestamp=datetime.now(),
                retrieved_documents=[result.document for result in search_results],
                similarity_scores=[result.similarity_score for result in search_results],
                context_used=context,
                accuracy_score=chat_response.accuracy_score
            )
            
        except Exception as e:
            raise HTTPException(f"RAG execution with conversation error: {str(e)}")
    
    def _prepare_context(self, search_results: List[VectorSearchResult]) -> str:
        """Prepare context from retrieved documents"""
        if not search_results:
            return "No relevant documents found."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"Document {i} (Similarity: {result.similarity_score:.3f}):\n{result.document.content}")
        
        return "\n\n".join(context_parts)
    
    def _create_enhanced_prompt(self, query: str, context: str) -> str:
        """Create enhanced prompt with context"""
        return f"""Based on the following context, please answer the user's question. If the context doesn't contain enough information to answer the question, please say so.

Context:
{context}

Question: {query}

Answer:"""
    
    def _create_enhanced_prompt_with_conversation(self, query: str, context: str, 
                                                conversation_messages: List[Dict[str, str]], 
                                                system_prompt: Optional[str] = None) -> str:
        """Create enhanced prompt with context and conversation history"""
        # Build conversation history
        conversation_text = ""
        if conversation_messages:
            conversation_parts = []
            for msg in conversation_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    conversation_parts.append(f"User: {content}")
                elif role == "assistant":
                    conversation_parts.append(f"Assistant: {content}")
            conversation_text = "\n".join(conversation_parts)
        
        # Create the enhanced prompt
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        
        if conversation_text:
            prompt_parts.append(f"Previous conversation:\n{conversation_text}")
        
        prompt_parts.append(f"Context from knowledge base:\n{context}")
        prompt_parts.append(f"Current question: {query}")
        prompt_parts.append("Please answer the current question based on the context and conversation history.")
        
        return "\n\n".join(prompt_parts)
    
    def _extract_text_content(self, doc: DocumentUpload) -> str:
        """Extract text content from Document object"""
        if hasattr(doc.content, 'page_content'):
            # If it's a Document object, extract the page_content
            return doc.content.page_content
        elif hasattr(doc.content, 'content'):
            # If it's a Document object with content attribute
            return doc.content.content
        elif isinstance(doc.content, str):
            # If it's already a string, use it as is
            return doc.content
        else:
            # Convert to string if it's some other object
            return str(doc.content)

    def _create_embedding_request(self, doc: DocumentUpload) -> EmbeddingRequest:
        """Create embedding request for document"""
        text_content = self._extract_text_content(doc)
        return EmbeddingRequest(
            text=text_content,
            user_id=doc.metadata.get('user_id', 'system'),
            metadata=doc.metadata
        )

    async def _process_document_embedding(self, doc: DocumentUpload, model_id: str = None, api_key: str = None) -> DocumentUpload:
        """Process document embedding with optional model_id override"""
        if doc.embedding:
            return doc
        
        embedding_request = self._create_embedding_request(doc)
        
        # If model_id is provided, update the embedding adapter's model
        original_model_id = None
        if model_id and hasattr(self.embedding_adapter, 'model_id'):
            original_model_id = self.embedding_adapter.model_id
            self.embedding_adapter.model_id = model_id
        
        try:
            embedding_response = await self.embedding_adapter.create_embedding(embedding_request, api_key)
            doc.embedding = embedding_response.embedding
        finally:
            # Restore original model_id if it was changed
            if original_model_id and hasattr(self.embedding_adapter, 'model_id'):
                self.embedding_adapter.model_id = original_model_id
        
        return doc

    async def _create_embeddings_for_documents(self, documents: List[DocumentUpload], model_id: str = None, api_key: str = None) -> List[DocumentUpload]:
        """Create embeddings for documents that don't have them"""

        documents_with_embeddings = []
        
        for doc in documents:
            processed_doc = await self._process_document_embedding(doc, model_id, api_key)
            documents_with_embeddings.append(processed_doc)
        
        return documents_with_embeddings

    async def _fix_dimension_mismatch(self, documents: List[DocumentUpload], target_dimension: int, model_id: str = None, api_key: str = None) -> List[DocumentUpload]:
        """Fix dimension mismatch by either resizing embeddings or recreating them with the correct model"""
        try:
            # First, try to resize the embeddings if possible
            resized_documents = await self._resize_embeddings(documents, target_dimension)
            if resized_documents:
                #print(f"Successfully resized embeddings from {len(documents[0].embedding)} to {target_dimension} dimensions")
                return resized_documents
            
            # If resizing fails, try to recreate embeddings with the correct model
            #print(f"Resizing failed, recreating embeddings with correct dimension {target_dimension}")
            return await self._recreate_embeddings_with_correct_dimension(documents, target_dimension, model_id, api_key)
            
        except Exception as e:
            raise ValueError(f"Failed to fix dimension mismatch: {str(e)}")

    async def _resize_embeddings(self, documents: List[DocumentUpload], target_dimension: int) -> List[DocumentUpload]:
        """Resize embeddings to match target dimension using interpolation"""
        try:
            import numpy as np
            
            resized_documents = []
            for doc in documents:
                if not doc.embedding:
                    continue
                
                embedding = np.array(doc.embedding)
                current_dim = len(embedding)
                
                if current_dim == target_dimension:
                    resized_documents.append(doc)
                    continue
                
                # Resize using interpolation
                if current_dim < target_dimension:
                    # Pad with zeros or repeat values
                    padding = np.zeros(target_dimension - current_dim)
                    resized_embedding = np.concatenate([embedding, padding])
                else:
                    # Truncate or sample
                    indices = np.linspace(0, current_dim - 1, target_dimension, dtype=int)
                    resized_embedding = embedding[indices]
                
                # Normalize the resized embedding
                norm = np.linalg.norm(resized_embedding)
                if norm > 0:
                    resized_embedding = resized_embedding / norm
                
                # Create new document with resized embedding
                resized_doc = DocumentUpload(
                    id=doc.id,
                    content=doc.content,
                    metadata=doc.metadata,
                    embedding=resized_embedding.tolist(),
                    createdattimestamp=doc.createdattimestamp,
                    lastupdatedtimestamp=datetime.now()
                )
                resized_documents.append(resized_doc)
            
            return resized_documents
        except Exception as e:
            #print(f"Resizing failed: {str(e)}")
            return []

    async def _recreate_embeddings_with_correct_dimension(self, documents: List[DocumentUpload], target_dimension: int, model_id: str = None, api_key: str = None) -> List[DocumentUpload]:
        """Recreate embeddings using a model that produces the correct dimension"""
        try:
            # Map target dimension to appropriate embedding model
            dimension_to_model = {
                1536: "text-embedding-3-small",  # or text-embedding-ada-002
                3072: "text-embedding-3-large"
            }
            
            target_model = dimension_to_model.get(target_dimension)
            if not target_model:
                raise ValueError(f"No embedding model available for dimension {target_dimension}")
            
            #print(f"Recreating embeddings using model: {target_model}")
            
            # Temporarily change the embedding model
            original_model = None
            if hasattr(self.embedding_adapter, 'embedding_model'):
                original_model = self.embedding_adapter.embedding_model
                self.embedding_adapter.embedding_model = target_model
            
            try:
                # Recreate embeddings for all documents
                recreated_documents = []
                for doc in documents:
                    # Create new embedding request
                    embedding_request = EmbeddingRequest(
                        text=self._extract_text_content(doc),
                        user_id=doc.metadata.get('user_id', 'system'),
                        metadata=doc.metadata
                    )
                    
                    # Create new embedding
                    embedding_response = await self.embedding_adapter.create_embedding(embedding_request, api_key)
                    
                    # Create new document with correct embedding
                    recreated_doc = DocumentUpload(
                        id=doc.id,
                        content=doc.content,
                        metadata=doc.metadata,
                        embedding=embedding_response.embedding,
                        createdattimestamp=doc.createdattimestamp,
                        lastupdatedtimestamp=datetime.now()
                    )
                    recreated_documents.append(recreated_doc)
                
                return recreated_documents
            finally:
                # Restore original model
                if original_model and hasattr(self.embedding_adapter, 'embedding_model'):
                    self.embedding_adapter.embedding_model = original_model
                    
        except Exception as e:
            raise ValueError(f"Failed to recreate embeddings: {str(e)}")

    async def _create_collection_if_needed(self, collection_name: str, embedding_model: str, dimension: int):
        """Create collection if it doesn't exist"""

        await self.vector_store.create_collection(
            name=collection_name,
            embedding_model=embedding_model or "default",
            metadata={"created_by": "rag_executor", "dimension": dimension}
        )

    async def add_documents_to_collection(self, collection_name: str, documents: List[DocumentUpload], embedding_model: str = None, model_id: str = None, api_key: str = None) -> bool:
        """Add documents to a collection with embeddings"""
        try:
            # Create embeddings for documents that don't have them
            documents_with_embeddings = await self._create_embeddings_for_documents(documents, model_id, api_key)
            dimension = len(documents_with_embeddings[0].embedding)
            #print("dimension", dimension)
            
            # Check if collection exists and get its expected dimension
            if hasattr(self.vector_store, 'get_collection_dimension'):
                existing_dimension = await self.vector_store.get_collection_dimension(collection_name)
                if existing_dimension and existing_dimension != dimension:
                    # Try to fix the dimension mismatch
                    documents_with_embeddings = await self._fix_dimension_mismatch(
                        documents_with_embeddings, 
                        existing_dimension, 
                        model_id, 
                        api_key
                    )
                    dimension = existing_dimension
            
            # Create collection if it doesn't exist
            await self._create_collection_if_needed(collection_name, embedding_model, dimension)
            #print("collection_name", collection_name)
            #print("embedding_model", embedding_model)
            #print("dimension", dimension)
            #print("documents_with_embeddings", documents_with_embeddings)
            
            # Add documents to vector store
            result = await self.vector_store.add_documents(collection_name, dimension, documents_with_embeddings)
            #print("result", result)
            return result
            
        except Exception as e:
            raise HTTPException(f"Error adding documents to collection: {str(e)}")