from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.corestructure.dataclass import ProviderEnum, VectorStoreEnum, EmbeddingModelEnum
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from app.corestructure.dataclass import ChatRequest, ChatResponse

LITERAL_API_KEY = "sk-..."
LITERAL_MODEL_ID = "gpt-3.5-turbo"
LITERAL_ADDITIONAL_METADATA = {"session_id": "session123"}
# Authentication request/response models
class LoginRequest(BaseModel):
    username: str
    password: str

class ValidateProviderApiKeyRequestSchema(BaseModel):
    provider: str = Field(..., description="LLM provider")
    api_key: Optional[str] = Field(None, description="API key for the provider (optional if stored)")
    username: str = Field(..., description="Username for validation")
    

# View and Display the list of providers and models
class ModelListRequestSchema(BaseModel):
    provider: str = Field(..., description="LLM provider")
    api_key: str = Field(..., description="API key for the provider")

    class Config:
        schema_extra = {
            "example": {
                "provider": "openai",
                "api_key": LITERAL_API_KEY
            }
        }

# Chat with the LLM / Query the LLM
class ChatRequestSchema(BaseModel):
    prompt: str # The input prompt for the LLM
    prompt_type: str # The type of prompt (text, image, audio, video)
    prompt_id: str # The ID of the prompt
    model_id: str # The model ID to use
    provider: str # LLM provider (openai, anthropic, azure, google)
    api_key: str # API key for the provider
    user_id: str # User identifier
    project_id: str # Project identifier
    session_id: str # Session identifier
    max_tokens: Optional[int] # Maximum tokens to generate
    temperature: Optional[float] # Temperature for response generation
    metadata: Optional[Dict[str, Any]] # Additional metadata
    
    # Conversation memory options
    use_conversation_memory: Optional[bool] = True # Whether to use conversation memory
    max_conversation_messages: Optional[int] = 10 # Maximum number of messages to include in context
    max_conversation_tokens: Optional[int] = None # Maximum tokens for conversation context
    system_prompt: Optional[str] = None # System prompt to prepend to conversation
    clear_conversation: Optional[bool] = False # Whether to clear conversation history
    
    # Streaming options
    stream: Optional[bool] = False # Whether to stream the response using SSE

    class Config:
        schema_extra = {
            "example": {
                "prompt": "What is the capital of France?",
                "prompt_type": "text",
                "prompt_id": "prompt123",
                "user_id": "user123",
                "project_id": "project123",
                "session_id": "session123",
                "model_id": LITERAL_MODEL_ID,
                "provider": "openai",
                "api_key": LITERAL_API_KEY,
                "max_tokens": 150,
                "temperature": 0.7,
                "metadata": {"session_id": "session123"},
                "use_conversation_memory": True,
                "max_conversation_messages": 10,
                "max_conversation_tokens": 2000,
                "system_prompt": "You are a helpful assistant.",
                "clear_conversation": False,
                "stream": False
            }
        }


#Embedding API
class EmbeddingRequestSchema(BaseModel):
    text: str # Text to create embedding for
    provider: str # Embedding provider (openai, sentence_transformers)
    api_key: str # API key for the provider
    model_id: str # The model ID to use
    provider_config: Optional[Dict[str, Any]] # Field(None, description="Provider-specific configuration")
    metadata: Optional[Dict[str, Any]] # Field(None, description="Additional metadata")

#Document Upload API
class DocumentUploadSchema(BaseModel):
    collection_name: str # Name of the collection to upload to
    documents: List[Dict[str, Any]] # List of documents to upload
    vector_store: str = Field(..., description="Vector store to use (chroma, faiss, pinecone)")
    embedding_model: str = Field(..., description="Embedding model to use (text-embedding-ada-002, text-embedding-004)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        schema_extra = {
            "example": {
                "collection_name": "my_documents",
                "vector_store": "chroma",
                "embedding_model": "text-embedding-ada-002",
                "documents": [
                    {
                        "content": "This is the content of document 1",
                        "source": "file1.txt",
                        "metadata": {"category": "technical"}
                    }
                ]
            }
        }

#RAG API
class RAGRequestSchema(BaseModel):
    query: str = Field(..., description="The query to answer")
    model_id: str = Field(..., description="The LLM model ID to use")
    llm_provider: ProviderEnum = Field(..., description="LLM provider (openai, anthropic)")
    llm_api_key: str = Field(..., description="API key for the LLM provider")
    embedding_provider: str = Field(..., description="Embedding provider (openai, sentence_transformers)")
    embedding_api_key: str = Field(..., description="API key for the embedding provider")
    collection_name: str = Field(..., description="Name of the collection to search")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Temperature for response generation")
    top_k: int = Field(5, description="Number of similar documents to retrieve")
    similarity_threshold: float = Field(0.7, description="Minimum similarity score for documents")
    embedding_config: Optional[Dict[str, Any]] = Field(None, description="Embedding provider configuration")
    metadata: Optional[Dict[str, Any]] = Field(None, description="metadata")
    vector_store: VectorStoreEnum = Field(..., description="Vector store to use (chroma, faiss, pinecone)")
    embedding_model: EmbeddingModelEnum = Field(..., description="Embedding model to use (text-embedding-ada-002, text-embedding-004)")

    # Conversation memory options for RAG
    use_conversation_memory: Optional[bool] = True # Whether to use conversation memory
    max_conversation_messages: Optional[int] = 10 # Maximum number of messages to include in context
    max_conversation_tokens: Optional[int] = None # Maximum tokens for conversation context
    system_prompt: Optional[str] = None # System prompt to prepend to conversation
    clear_conversation: Optional[bool] = False # Whether to clear conversation history
    session_id: Optional[str] = None # Session identifier for conversation memory
    user_id: Optional[str] = None # User identifier for conversation memory
    project_id: Optional[str] = None # Project identifier for conversation memory
    
    # Streaming options
    stream: Optional[bool] = False # Whether to stream the response using SSE
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "vector_store": "chroma",
                "embedding_model": "text-embedding-ada-002",
                "model_id": LITERAL_MODEL_ID,
                "llm_provider": "openai",
                "llm_api_key": LITERAL_API_KEY,
                "embedding_provider": "openai",
                "embedding_api_key": LITERAL_API_KEY,
                "collection_name": "ml_documents",
                "max_tokens": 150,
                "temperature": 0.7,
                "top_k": 5,
                "similarity_threshold": 0.7,
                "model": "gemini-1.5-flash",
                "use_conversation_memory": True,
                "max_conversation_messages": 10,
                "max_conversation_tokens": 2000,
                "system_prompt": "You are a helpful assistant with access to knowledge base.",
                "clear_conversation": False,
                "session_id": "session123",
                "user_id": "user123",
                "project_id": "project123",
                "stream": False
            }
        }

class MetricsRequestSchema(BaseModel):
    user_id: Optional[str] = Field(None, description="User ID to filter metrics")
    project_id: Optional[str] = Field(None, description="Project ID to filter metrics")
    period: str = Field(..., description="Time period: 'day', 'week', or 'month'")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "project_id": "project456",
                "period": "week"
            }
        }

class UserProjectsRequestSchema(BaseModel):
    user_id: str = Field(..., description="User ID to get projects for")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123"
            }
        }

class ProjectUsersRequestSchema(BaseModel):
    project_id: str = Field(..., description="Project ID to get users for")
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "project456"
            }
        }

class SuccessfulHitsRequestSchema(BaseModel):
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    project_id: Optional[str] = Field(None, description="Filter by project ID")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "project_id": "project456",
                "limit": 50,
                "offset": 0
            }
        }

class SuccessfulHitsSummaryRequestSchema(BaseModel):
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    project_id: Optional[str] = Field(None, description="Filter by project ID")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "project_id": "project456"
            }
        }

# Conversation Memory Management APIs
class ConversationSessionRequestSchema(BaseModel):
    session_id: str = Field(..., description="Session ID to manage")
    user_id: str = Field(..., description="User ID")
    project_id: str = Field(..., description="Project ID")
    model_id: str = Field(..., description="Model ID")
    provider: str = Field(..., description="Provider name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ConversationHistoryRequestSchema(BaseModel):
    session_id: str = Field(..., description="Session ID to get history for")
    max_messages: Optional[int] = Field(10, description="Maximum number of messages to retrieve")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for conversation context")

class ConversationSummaryRequestSchema(BaseModel):
    session_id: str = Field(..., description="Session ID to get summary for")

class UserSessionsRequestSchema(BaseModel):
    user_id: str = Field(..., description="User ID to get sessions for")
    limit: Optional[int] = Field(50, description="Maximum number of sessions to retrieve")

class DeleteSessionRequestSchema(BaseModel):
    session_id: str = Field(..., description="Session ID to delete")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "session123"
            }
        }

class UsageLogsRequestSchema(BaseModel):
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    project_id: Optional[str] = Field(None, description="Filter by project ID")
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    group_by: str = Field("date", description="Group by: 'date', 'model', 'provider', or 'date_model_provider'")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "project_id": "project123",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "group_by": "date_model_provider"
            }
        }

