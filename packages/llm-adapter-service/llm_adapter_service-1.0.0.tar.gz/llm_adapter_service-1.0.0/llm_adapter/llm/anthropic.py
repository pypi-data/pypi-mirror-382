import anthropic
import time
import json
import os
from fastapi import HTTPException
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime
from app.llm.base import BaseLLMAdapter
from app.corestructure.dataclass import ModelInfo, ChatRequest, ChatResponse, EmbeddingRequest, EmbeddingResponse, ProviderType, llmdata
import requests


class AnthropicAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.embedding_model = kwargs.get('embedding_model', 'claude-3-sonnet-20240229')
        self.model = kwargs.get('model', 'claude-3-sonnet-20240229')
    
    """Validate Connection using API key for a test message"""
    async def validate_connection(self) -> bool:
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Common Basic Model
                max_tokens=100,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            ##print(f"Anthropic validation error: {str(e)}")
            return False
            
    """Validate EmbeddingConnection using API key for a test message"""
    async def validate_embedding_connection(self) -> bool:
        try:
            # Anthropic doesn't have a direct embedding API, so we'll use a simple text generation test
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            return False
    
    """List available Anthropic models"""
    async def list_models(self) -> List[ModelInfo]:
        try:
            models = self.client.models.list(limit=20)

            model_list = []
            for model in models.data: 
                model_info = ModelInfo(
                    id=model.id,
                    name=getattr(model, 'display_name', None),  # Use display_name as name
                    provider=getattr(model, 'provider', ProviderType.ANTHROPIC),  
                    max_tokens=getattr(model, 'max_tokens', llmdata.MAX_TOKENS.value),  
                    cost_per_token=getattr(model, 'cost_per_token', llmdata.DEFAULT_COST_PER_TOKEN.value),  
                    capabilities=getattr(model, 'capabilities', llmdata.CAPABILITIES.value)  
                )
                model_list.append(model_info)
            return model_list
        except Exception as e:
            raise HTTPException(f"Models list error: {str(e)}")
    
    """List available Anthropic embedding models"""
    async def list_embedding_models(self) -> List[ModelInfo]:
        try:
            # Anthropic doesn't have dedicated embedding models, but we can use their text models for embeddings
            models = self.client.models.list(limit=20)
            model_list = []
            
            # Filter for models that can be used for embeddings (text models)
            embedding_models = [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229", 
                "claude-3-haiku-20240307"
            ]
            
            for model in models.data:
                if model.id in embedding_models:
                    model_info = ModelInfo(
                        id=model.id,
                        name=getattr(model, 'display_name', model.id),
                        provider=getattr(model, 'provider', ProviderType.ANTHROPIC),  
                        max_tokens=getattr(model, 'max_tokens', llmdata.MAX_TOKENS.value),  
                        cost_per_token=getattr(model, 'cost_per_token', llmdata.DEFAULT_COST_PER_TOKEN.value),  
                        capabilities=getattr(model, 'capabilities', llmdata.EMBEDDING_CAPABILITIES.value) 
                    )
                    model_list.append(model_info)
            return model_list
        except Exception as e:
            raise HTTPException(f"Failed to list Anthropic embedding models: {str(e)}")
    
    """Chat Completion"""
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        
        try:
            response = self.client.messages.create(
                model=request.model_id,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature or 0.7,
                messages=[
                    {"role": "user", "content": request.prompt}
                ]
            )
            
            end_time = time.time()
            
            # Calculate accuracy score (Anthropic doesn't provide logprobs, so we'll use a default)
            accuracy_score = 0.0  # Default accuracy for Anthropic
            
            return ChatResponse(
                response=response.content[0].text,
                model_used=request.model_id,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                cost=self._calculate_cost(
                    response.usage.input_tokens, 
                    response.usage.output_tokens, 
                    request.model_id
                ),
                response_time=end_time - start_time,
                safety_score=0.8,  # Will be calculated by safety module
                timestamp=datetime.now(),
                accuracy_score=accuracy_score
            )
        except Exception as e:
            raise HTTPException(f"Anthropic API error: {str(e)}")
    
    """ Streaming Chat Completion using Anthropic models with cumulative word-by-word streaming """
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
            # Create streaming response
            stream = self.client.messages.stream(
                model=request.model_id,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature or 0.7,
                messages=[
                    {"role": "user", "content": request.prompt}
                ]
            )

            # Buffer for word-by-word streaming
            buffer = ""

            # Yield each chunk as SSE format with word-by-word processing
            for chunk in stream:
                if chunk.type == "content_block_delta":
                    buffer += chunk.delta.text
                    
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
    
    """Get max tokens for a model"""
    def _get_max_tokens(self, model_id: str) -> int:
        model_limits = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000
        }
        return model_limits.get(model_id, 200000)
    
    """Get cost per token for a model"""
    def _get_cost_per_token(self, model_id: str) -> float:
        # Cost per token for Anthropic models
        costs = {
            "claude-3-opus-20240229": 0.000015,  # Input tokens
            "claude-3-sonnet-20240229": 0.000003,  # Input tokens
            "claude-3-haiku-20240307": 0.00000025  # Input tokens
        }
        return costs.get(model_id, 0.000003)
    
    """Calculate cost based on input and output tokens"""
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        """Calculate cost based on input and output tokens"""
        cost_per_input_token = {
            "claude-3-opus-20240229": 0.000015,
            "claude-3-sonnet-20240229": 0.000003,
            "claude-3-haiku-20240307": 0.00000025
        }
        
        cost_per_output_token = {
            "claude-3-opus-20240229": 0.000075,
            "claude-3-sonnet-20240229": 0.000015,
            "claude-3-haiku-20240307": 0.00000125
        }
        
        input_cost = input_tokens * cost_per_input_token.get(model_id, 0.000003)
        output_cost = output_tokens * cost_per_output_token.get(model_id, 0.000015)
        
        return input_cost + output_cost
    
    """Create embedding for the given text using Anthropic's text generation"""
    async def create_embedding(self, request: EmbeddingRequest, api_key: str) -> EmbeddingResponse:
        try:

            start_time = time.time()
            
            # Since Anthropic doesn't have a direct embedding API, we'll use text generation
            # to create a semantic representation that can be used as an embedding
            prompt = f"""Please analyze the following text and provide a semantic summary that captures its key meaning and context. Return only the summary without any additional text:

Text: {request.text}

Semantic Summary:"""
            
            response = self.client.messages.create(
                model=self.embedding_model,
                max_tokens=200,
                temperature=0.1,  # Low temperature for consistent output
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Convert the semantic summary to a numerical representation
            # This is a simplified approach - in production, you might want to use a proper embedding service
            semantic_text = response.content[0].text
            
            # Create a simple hash-based embedding (this is a placeholder)
            # In a real implementation, you'd use a proper embedding service
            embedding = self._text_to_embedding(semantic_text)
            
            end_time = time.time()
            
            return EmbeddingResponse(
                embedding=embedding,
                model_used=self.embedding_model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                cost=self._calculate_cost(
                    response.usage.input_tokens, 
                    response.usage.output_tokens, 
                    self.embedding_model
                ),
                response_time=end_time - start_time,
                timestamp=datetime.now()
            )
        except Exception as e:
            raise HTTPException(f"Anthropic Embedding API error: {str(e)}")

    """Create embeddings for multiple texts"""
    async def create_embeddings_batch(self, requests: List[EmbeddingRequest], api_key: str) -> List[EmbeddingResponse]:
        try:
            start_time = time.time()
            responses = []
            
            for req in requests:
                response = await self.create_embedding(req, api_key)
                responses.append(response)
            
            end_time = time.time()
            
            # Adjust response times for batch processing
            for response in responses:
                response.response_time = end_time - start_time
                
            return responses
        except Exception as e:
            raise HTTPException(f"Anthropic Embedding Batch API error: {str(e)}")

    def _text_to_embedding(self, text: str) -> List[float]:
        """Convert text to a numerical embedding representation"""
        # This is a simplified implementation
        # In production, you should use a proper embedding service or model
        
        # Create a simple hash-based embedding
        import hashlib
        import struct
        
        # Hash the text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to list of floats (1536 dimensions like OpenAI embeddings)
        embedding = []
        for i in range(0, min(len(hash_bytes), 1536 * 4), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                float_val = struct.unpack('f', chunk)[0]
                embedding.append(float_val)
            else:
                # Pad with zeros if needed
                embedding.append(0.0)
        
        # Ensure we have exactly 1536 dimensions
        while len(embedding) < 1536:
            embedding.append(0.0)
        
        return embedding[:1536]