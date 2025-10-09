from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import base64
from dataclasses import dataclass, asdict
from app.corestructure.dataclass import ChatRequest, ChatResponse
from io import BytesIO
LITERAL_MODEL_ID = "gpt-3.5-turbo"



class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    expires_in: int
    
#For the provider, list the models available
class ModelInfoSchema(BaseModel):
    id: str
    name: str
    provider: str
    max_tokens: int
    cost_per_token: float
    capabilities: List[str]

    class Config:
        schema_extra = {
            "example": {
                "id": LITERAL_MODEL_ID,
                "name": "GPT-3.5 Turbo",
                "provider": "openai",
                "max_tokens": 4096,
                "cost_per_token": 0.000002,
                "capabilities": ["chat", "completion"]
            }
        }

#Basic List of Providers 
class ModelListResponseSchema(BaseModel):
    models: List[ModelInfoSchema]
    total_count: int

#API Key Validation Response
class ApiKeyValidationResponseSchema(BaseModel):
    api_key_found: bool
    api_key_valid: bool
    models: List[ModelInfoSchema]
    total_count: int
    message: str

class ConversationMessage(BaseModel):
    role: str
    content: str
    tokens_used: Optional[int] = 0
    cost: Optional[float] = 0.0
    timestamp: Optional[str] = None

#Chat Response from the LLM
class ChatResponseSchema(BaseModel):
    request_id: str
    project_id: str
    session_id: str
    user_id: str
    prompt_id: str
    prompt_type: str
    response: str
    response_image: Optional[Union[str, bytes]] = None
    model_used: str
    tokens_used: int
    cost: float
    response_time: float
    safety_score: float
    timestamp: datetime
    accuracy_score: float
    
    # Conversation memory information
    conversation_message_count: Optional[int] = None
    conversation_total_tokens: Optional[int] = None
    conversation_total_cost: Optional[float] = None
    conversation_context: Optional[List[Dict[str,str]]] = None
    class Config:
        schema_extra = {
            "example": {
                "request_id": "req-123",
                "project_id": "proj-123",
                "session_id": "sess-123",
                "user_id": "user-123",
                "prompt_id": "prompt-123",
                "prompt_type": "text",
                "response": "The capital of France is Paris.",
                "model_used": LITERAL_MODEL_ID,
                "tokens_used": 25,
                "cost": 0.00005,
                "response_time": 1.2,
                "safety_score": 0.95,
                "timestamp": "2023-01-01T12:00:00",
                "accuracy_score": 0.0,
                "conversation_message_count": 2,
                "conversation_total_tokens": 100,
                "conversation_total_cost": 0.00005,
                "conversation_context": [
                    {"role": "user", "content": "....."},
                    {"role": "assistant", "content": "....."}
                ]
            }
        }

class EmbeddingResponseSchema(BaseModel):
    embedding: List[float]  #The embedding vector
    model_used: str #Model used for embedding
    tokens_used: int #Number of tokens used
    cost: float #Cost of the embedding
    response_time: float #Response time in seconds
    timestamp: datetime #Timestamp of the response

class CollectionInfoSchema(BaseModel):
    name: str #Collection name
    document_count: int #Number of documents in collection
    embedding_model: str #Embedding model used
    createdattimestamp: datetime #Creation timestamp
    lastupdatedtimestamp: datetime #Last update timestamp
    metadata: Dict[str, Any] #Collection metadata

class RAGResponseSchema(BaseModel):
    response: str #The generated response
    model_used: str #Model used for generation
    tokens_used: int #Number of tokens used
    cost: float #Total cost
    response_time: float #Response time in seconds
    safety_score: float #Safety score
    timestamp: datetime #Timestamp of the response
    accuracy_score: Optional[float] = None #Accuracy score from logprobs
    retrieved_documents: List[Dict[str, Any]] #Retrieved documents
    similarity_scores: List[float] #Similarity scores
    context_used: str #Context used for generation
    
    # Conversation memory information
    conversation_message_count: Optional[int] = None
    conversation_total_tokens: Optional[int] = None
    conversation_total_cost: Optional[float] = None

#Safety Check Response
class SafetyCheckResponseSchema(BaseModel):
    is_safe: bool
    safety_level: str
    flagged_keywords: List[str]
    confidence_score: float
    reason: Optional[str] = None

#Metrics Response
class ModelBreakdownSchema(BaseModel):
    cost: float
    tokens: int
    requests: int

class MetricsResponseSchema(BaseModel):
    period: str
    start_date: str
    end_date: str
    user_id: Optional[str]
    project_id: Optional[str]
    total_cost: float
    total_tokens: int
    total_input_tokens: int
    total_output_tokens: int
    total_requests: int
    model_breakdown: Dict[str, ModelBreakdownSchema]
    average_cost_per_request: float
    average_tokens_per_request: float
    
    class Config:
        schema_extra = {
            "example": {
                "period": "week",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-01-08T00:00:00",
                "user_id": "user123",
                "project_id": "project456",
                "total_cost": 0.0025,
                "total_tokens": 1500,
                "total_input_tokens": 800,
                "total_output_tokens": 700,
                "total_requests": 10,
                "model_breakdown": {
                    LITERAL_MODEL_ID: {
                        "cost": 0.0025,
                        "tokens": 1500,
                        "requests": 10
                    }
                },
                "average_cost_per_request": 0.00025,
                "average_tokens_per_request": 150.0
            }
        }

class UserProjectsResponseSchema(BaseModel):
    user_id: str
    projects: List[str]
    total_projects: int
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "projects": ["project1", "project2", "project3"],
                "total_projects": 3
            }
        }

class ProjectUsersResponseSchema(BaseModel):
    project_id: str
    users: List[str]
    total_users: int
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "project456",
                "users": ["user1", "user2", "user3"],
                "total_users": 3
            }
        }

#Health Check Response
class HealthCheckResponseSchema(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: float
    providers_status: Dict[str, bool]

@dataclass
class ConversationMessage:
    """Represents a single message in a conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    message_id: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ConversationSession:
    """Represents a conversation session"""
    session_id: str
    user_id: str
    project_id: str
    model_id: str
    provider: str
    created_at: datetime
    last_updated: datetime
    message_count: int
    total_tokens: int
    total_cost: float
    metadata: Optional[Dict[str, Any]] = None

# Conversation Memory Response Schemas
class ConversationSessionResponseSchema(BaseModel):
    session_id: str
    user_id: str
    project_id: str
    model_id: str
    provider: str
    created_at: datetime
    last_updated: datetime
    message_count: int
    total_tokens: int
    total_cost: float
    metadata: Optional[Dict[str, Any]] = None

class ConversationHistoryResponseSchema(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    total_messages: int
    total_tokens: int

class ConversationSummaryResponseSchema(BaseModel):
    session_id: str
    user_id: str
    project_id: str
    model_id: str
    provider: str
    created_at: datetime
    last_updated: datetime
    message_count: int
    total_tokens: int
    total_cost: float
    duration_hours: float
    average_tokens_per_message: float
    average_cost_per_message: float

class UserSessionsResponseSchema(BaseModel):
    user_id: str
    sessions: List[ConversationSessionResponseSchema]
    total_sessions: int

class DeleteSessionResponseSchema(BaseModel):
    session_id: str
    success: bool
    message: str

    class Config:
        schema_extra = {
            "example": {
                "session_id": "session123",
                "success": True,
                "message": "Session deleted successfully"
            }
        }

class UsageLogEntrySchema(BaseModel):
    date: str
    model_id: Optional[str] = None
    provider: Optional[str] = None
    total_cost: float
    total_tokens: int
    request_count: int
    average_cost_per_request: float
    average_tokens_per_request: float
    average_safety_score: float
    average_response_time: float

    class Config:
        schema_extra = {
            "example": {
                "date": "2024-01-15",
                "model_id": "gpt-4",
                "provider": "openai",
                "total_cost": 0.125,
                "total_tokens": 5000,
                "request_count": 25,
                "average_cost_per_request": 0.005,
                "average_tokens_per_request": 200
            }
        }

class UsageLogsResponseSchema(BaseModel):
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    group_by: str
    total_cost: float
    total_tokens: int
    total_requests: int
    entries: List[UsageLogEntrySchema]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "project_id": "project123",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "group_by": "date_model_provider",
                "total_cost": 1.25,
                "total_tokens": 50000,
                "total_requests": 250,
                "entries": [
                    {
                        "date": "2024-01-15",
                        "model_id": "gpt-4",
                        "provider": "openai",
                        "total_cost": 0.125,
                        "total_tokens": 5000,
                        "request_count": 25,
                        "average_cost_per_request": 0.005,
                        "average_tokens_per_request": 200,
                        "average_safety_score": 0.95,
                        "average_response_time": 1.2
                    }
                ]
            }
        }