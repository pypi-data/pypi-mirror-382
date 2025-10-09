import httpx
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path

from .schemas.request import (
    LoginRequest, ChatRequestSchema, RAGRequestSchema
)
from .schemas.response import (
    LoginResponse, ChatResponseSchema, RAGResponseSchema
)
from .exceptions import LLMAdapterError, AuthenticationError, APIError

class LLMAdapterClient:
    """Client for LLM Adapter Service API"""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:3000",
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = timeout
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def login(
        self, 
        username: Optional[str] = None, 
        password: Optional[str] = None
    ) -> LoginResponse:
        """Authenticate and get JWT token"""
        username = username or self.username
        password = password or self.password
        
        if not username or not password:
            raise AuthenticationError("Username and password required")
        
        request = LoginRequest(username=username, password=password)
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/login",
                json=request.dict()
            )
            response.raise_for_status()
            
            login_response = LoginResponse(**response.json())
            self.token = login_response.access_token
            return login_response
            
        except httpx.HTTPStatusError as e:
            raise APIError(f"Login failed: {e.response.text}")
        except Exception as e:
            raise LLMAdapterError(f"Login error: {str(e)}")
    
    async def query_llm(self, request: ChatRequestSchema) -> ChatResponseSchema:
        """Query LLM with conversation memory"""
        await self._ensure_authenticated()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/query_llm",
                json=request.dict(),
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            return ChatResponseSchema(**response.json())
            
        except httpx.HTTPStatusError as e:
            raise APIError(f"LLM query failed: {e.response.text}")
    
    async def query_rag(self, request: RAGRequestSchema) -> RAGResponseSchema:
        """Execute RAG query with conversation memory"""
        await self._ensure_authenticated()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/query_rag",
                json=request.dict(),
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            return RAGResponseSchema(**response.json())
            
        except httpx.HTTPStatusError as e:
            raise APIError(f"RAG query failed: {e.response.text}")
    
    async def query_rag_chunks(self, request: RAGRequestSchema) -> List[Dict]:
        """Retrieve chunks from vector DB (no LLM call)"""
        await self._ensure_authenticated()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/query_rag_chunks",
                json=request.dict(),
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise APIError(f"RAG chunks query failed: {e.response.text}")
    
    async def upload_file(
        self,
        file_path: str,
        vector_store: str,
        collection_name: str,
        embedding_provider: str,
        model_id: str,
        embedding_model: str,
        embedding_api_key: str,
        metadata: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload file to vector store"""
        await self._ensure_authenticated()
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                files = {"file": (file_path.name, f, "application/octet-stream")}
                data = {
                    "vector_store": vector_store,
                    "collection_name": collection_name,
                    "embedding_provider": embedding_provider,
                    "model_id": model_id,
                    "embedding_model": embedding_model,
                    "embedding_api_key": embedding_api_key,
                }
                if metadata:
                    data["metadata"] = metadata
                
                response = await self.client.post(
                    f"{self.base_url}/api/v1/upload_file",
                    files=files,
                    data=data,
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            raise APIError(f"File upload failed: {e.response.text}")
    
    async def _ensure_authenticated(self):
        """Ensure client is authenticated"""
        if not self.token:
            if self.username and self.password:
                await self.login()
            else:
                raise AuthenticationError("Not authenticated and no credentials provided")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()