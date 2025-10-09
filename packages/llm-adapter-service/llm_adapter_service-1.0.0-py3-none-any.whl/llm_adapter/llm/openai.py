from openai import OpenAI
from fastapi import HTTPException
import time
import json
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
from app.llm.base import BaseLLMAdapter
from app.corestructure.dataclass import ModelInfo, ChatRequest, ChatResponse, ProviderType, llmdata, EmbeddingRequest, EmbeddingResponse
from app.schema.request import EmbeddingRequestSchema
from app.schema.response import EmbeddingResponseSchema
from app.vectorstore.chroma import ChromaVectorStore

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)

        self.client = OpenAI(api_key=api_key)
        self.embedding_model = kwargs.get('embedding_model', 'text-embedding-ada-002')
        self.model_id = kwargs.get('model_id', 'gpt-4')
    
    """Validate Connection using API key for a test message"""
    async def validate_connection(self) -> bool:
        try:
            #await self.client.models.list()
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            return False

    """Validate EmbeddingConnection using API key for a test message"""
    async def validate_embedding_connection(self) -> bool:
        try:
  
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input="test"
            )
            return True
        except Exception as e:
            return False

    
    """ Lists all available OpenAI models associated with the provided API key """
    async def list_models(self) -> List[ModelInfo]:
        try:
            models = self.client.models.list()
            model_list = []
            
            for model in models.data:
                if 'gpt' in model.id and model.owned_by.lower() == "openai":  # Filter for chat models
                    model_info = ModelInfo(
                        id=model.id,
                        name=model.id,
                        provider=getattr(model, 'provider', ProviderType.OPENAI),  
                        max_tokens=getattr(model, 'max_tokens', llmdata.MAX_TOKENS.value),  
                        cost_per_token=getattr(model, 'cost_per_token', llmdata.DEFAULT_COST_PER_TOKEN.value),  
                        capabilities=getattr(model, 'capabilities', llmdata.EMBEDDING_CAPABILITIES.value) 
                        )
                    model_list.append(model_info)
            
            return model_list
        except Exception as e:
            raise HTTPException(f"Failed to list OpenAI models: {str(e)}")
    
    """ Lists all available OpenAI models associated with the provided API key """
    async def list_embedding_models(self) -> List[ModelInfo]:
        try:
            models = self.client.models.list()
            model_list = []
            embedding_keywords = ['embedding', 'embed', 'text-embedding']
            for model in models.data:
                if any(keyword in model.id.lower() for keyword in embedding_keywords): # Filter for embedding models
                    model_info = ModelInfo(
                        id=model.id,
                        name=model.id,
                        provider=getattr(model, 'provider', ProviderType.OPENAI),  
                        max_tokens=getattr(model, 'max_tokens', llmdata.MAX_TOKENS.value),  
                        cost_per_token=getattr(model, 'cost_per_token', llmdata.DEFAULT_COST_PER_TOKEN.value),  
                        capabilities=getattr(model, 'capabilities', llmdata.CAPABILITIES.value) 
                        )

                    model_list.append(model_info)
            return model_list
        except Exception as e:
            raise HTTPException(f"Failed to list OpenAI models: {str(e)}")
    
    """ Chat Completion using OpenAI models associated with the provided API key """
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        
        try:

            # Prepare messages for the API call
            messages = []

            # Add system message if provided
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})

            # Add conversation history if provided
            if request.conversation_messages:
                messages.extend(request.conversation_messages)

            
            # Add current user message
            messages.append({"role": "user", "content": request.prompt})

            response = self.client.chat.completions.create(
                model=request.model_id,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature or 0.7,
                logprobs=True,
                top_logprobs=5
            )
            end_time = time.time()
            # Calculate accuracy score from logprobs
            accuracy_score = self._calculate_accuracy_from_logprobs(response)
            
            return ChatResponse(
                response=response.choices[0].message.content,
                model_used=request.model_id,
                tokens_used=response.usage.total_tokens,
                cost=self._calculate_cost(response.usage.total_tokens, request.model_id),
                response_time=end_time - start_time,
                safety_score=0.8,  # Will be calculated by safety module
                timestamp=datetime.now(),
                accuracy_score=accuracy_score
            )
        except Exception as e:
            raise HTTPException(f"OpenAI API error: {str(e)}")
    
    """ Streaming Chat Completion using OpenAI models with cumulative word-by-word streaming """
    def clean_markdown(self, text: str) -> str:
        """Remove markdown formatting from text using regex"""
        if not text:
            return text
        
        import re
        # Remove bold markdown (**text** → text)
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        # Remove italic markdown (*text* → text)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        return text.strip()
    
    async def chat_completion_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        try:
            # Prepare messages for the API call
            messages = []

            # Add system message if provided
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})

            # Add conversation history if provided
            if request.conversation_messages:
                messages.extend(request.conversation_messages)

            # Add current user message
            messages.append({"role": "user", "content": request.prompt})

            # Create streaming response
            stream = self.client.chat.completions.create(
                model=request.model_id,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature or 0.7,
                stream=True
            )

            # Buffer for word-by-word streaming
            buffer = ""
            
            # Yield each chunk as SSE format with word-by-word processing
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    buffer += chunk.choices[0].delta.content
                    
                    # Process buffer word by word
                    words = buffer.split()
                    if len(words) > 1:  # If we have complete words
                        # Send each complete word individually
                        for word in words[:-1]:
                            # Clean markdown formatting from word
                            clean_word = self.clean_markdown(word)
                            if clean_word:  # Only send if word is not empty after cleaning
                                data = {
                                    "content": clean_word,
                                    "model": request.model_id,
                                    "timestamp": datetime.now().isoformat()
                                }
                                yield f"data: {json.dumps(data)}\n\n"
                        
                        # Keep the last word in buffer (might be incomplete)
                        buffer = words[-1]
                    elif len(words) == 1 and buffer.strip():
                        # Send partial word as it's being typed
                        clean_word = self.clean_markdown(buffer)
                        if clean_word:
                            data = {
                                "content": clean_word,
                                "model": request.model_id,
                                "timestamp": datetime.now().isoformat()
                            }
                            yield f"data: {json.dumps(data)}\n\n"
            
            # Send final word if there's any remaining content
            if buffer.strip():
                clean_word = self.clean_markdown(buffer.strip())
                if clean_word:
                    data = {
                        "content": clean_word,
                        "model": request.model_id,
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(data)}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done', 'timestamp': datetime.now().isoformat()})}\n\n"
            
        except Exception as e:
            # Send error as SSE
            error_data = {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    """Create embedding for the given text"""
    async def create_embedding(self, request: EmbeddingRequest, api_key: str) -> EmbeddingResponse:
        try:
            start_time = time.time()
            
            # Extract text content from Document object if needed
            text_content = request.text
            if hasattr(request.text, 'page_content'):
                # If it's a Document object, extract the page_content
                text_content = request.text.page_content
            elif hasattr(request.text, 'content'):
                # If it's a Document object with content attribute
                text_content = request.text.content
            elif isinstance(request.text, str):
                # If it's already a string, use it as is
                text_content = request.text
            else:
                # Convert to string if it's some other object
                text_content = str(request.text)
            
            response = self.client.embeddings.create(
                model=self.embedding_model,   
                input=text_content,
                encoding_format="float"
            )
            end_time = time.time()
            return EmbeddingResponse(
                embedding=response.data[0].embedding,
                model_used=self.model_id,
                tokens_used=response.usage.total_tokens,
                cost=self._calculate_cost(response.usage.total_tokens, self.model_id),
                response_time=end_time - start_time,
                timestamp=datetime.now()
            )
        except Exception as e:
            raise HTTPException(f"OpenAI Embedding API error: {str(e)}")
    
    """Create embeddings for multiple texts"""
    async def create_embeddings_batch(self, requests: List[EmbeddingRequest], api_key: str) -> List[EmbeddingResponse]:
        try:
            start_time = time.time()
            
            # Extract text content from EmbeddingRequest objects
            texts = []
            for req in requests:
                text_content = req.text
                if hasattr(req.text, 'page_content'):
                    # If it's a Document object, extract the page_content
                    text_content = req.text.page_content
                elif hasattr(req.text, 'content'):
                    # If it's a Document object with content attribute
                    text_content = req.text.content
                elif isinstance(req.text, str):
                    # If it's already a string, use it as is
                    text_content = req.text
                else:
                    # Convert to string if it's some other object
                    text_content = str(req.text)
                texts.append(text_content)
            
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts,
                encoding_format="float"
            )
            end_time = time.time()
            return [
                EmbeddingResponse(
                    embedding=response.data[i].embedding,
                    model_used=self.model_id,  
                    tokens_used=response.usage.total_tokens,
                    cost=self._calculate_cost(response.usage.total_tokens, self.model_id),
                    response_time=end_time - start_time,
                    timestamp=datetime.now()
                )
                for i in range(len(requests))
            ]
        except Exception as e:
            raise HTTPException(f"OpenAI Embedding Batch API error: {str(e)}")
    
    def _get_max_tokens(self, model_id: str) -> int:
        model_limits = {
            "gpt-4": 8192,
            "gpt-3.5-turbo": 4096,
            "text-embedding-3-small": 1000,
            "text-embedding-3-large": 2000
        }
        return model_limits.get(model_id, 4096)
    
    def _get_cost_per_token(self, model_id: str) -> float:
        # Simplified cost calculation (per 1K tokens)
        costs = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "text-embedding-3-small": 0.0001,
            "text-embedding-3-large": 0.0002
        }
        return costs.get(model_id, 0.002) / 1000
    
    def _calculate_cost(self, tokens: int, model_id: str) -> float:
        return tokens * self._get_cost_per_token(model_id)
    
    def _calculate_accuracy_from_logprobs(self, response) -> float:
        """Calculate accuracy score from logprobs"""
        try:
            if not hasattr(response.choices[0], 'logprobs') or not response.choices[0].logprobs:
                return 0.0
            
            # Extract logprobs from the response
            logprobs = response.choices[0].logprobs
            if not logprobs.content:
                return 0.0
            
            # Calculate average log probability
            total_logprob = 0.0
            token_count = 0
            
            for token_logprob in logprobs.content:
                if hasattr(token_logprob, 'logprob') and token_logprob.logprob is not None:
                    total_logprob += token_logprob.logprob
                    token_count += 1
            
            if token_count == 0:
                return 0.0
            
            # Convert log probability to probability and then to accuracy score
            avg_logprob = total_logprob / token_count
            probability = 2.71828 ** avg_logprob  # e^logprob
            
            # Convert to accuracy score (0-1 scale)
            accuracy_score = max(0.0, min(1.0, probability))
            
            return accuracy_score
            
        except Exception as e:
            return 0.0