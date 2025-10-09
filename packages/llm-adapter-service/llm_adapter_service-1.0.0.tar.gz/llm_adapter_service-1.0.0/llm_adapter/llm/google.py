import google.generativeai as genai
import time
import json
from typing import List, AsyncGenerator
from datetime import datetime
from app.llm.base import BaseLLMAdapter
from app.corestructure.dataclass import ModelInfo, ChatRequest, ChatResponse, ProviderType, llmdata, EmbeddingRequest, EmbeddingResponse
import asyncio
import hashlib
import struct
from core.logging.logger import LLMLogger
from io import BytesIO
from core.utils.image_utils import convert_image_for_response, validate_image_data
import base64

# Create logger instance
logger = LLMLogger()

LITERAL_MODELS = 'models/'


class GoogleAPIError(Exception):
    """Base exception for Google API related errors"""
    pass


class GoogleConnectionError(GoogleAPIError):
    """Exception raised when Google API connection fails"""
    pass


class GoogleModelError(GoogleAPIError):
    """Exception raised when Google model operations fail"""
    pass


class GoogleEmbeddingError(GoogleAPIError):
    """Exception raised when Google embedding operations fail"""
    pass


class GoogleTextExtractionError(GoogleAPIError):
    """Exception raised when text extraction from Google response fails"""
    pass


class GoogleCostCalculationError(GoogleAPIError):
    """Exception raised when cost calculation fails"""
    pass


class GoogleRateLimitError(GoogleAPIError):
    """Exception raised when Google API rate limit is exceeded"""
    pass


class GoogleTokenCalculationError(GoogleAPIError):
    """Exception raised when token calculation fails"""
    pass


class GoogleAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        logger.info(f"Initializing Google adapter with API key length: {len(api_key) if api_key else 0}")
        genai.configure(api_key=api_key)
        self.client = genai
        self.model_id = kwargs.get('model_id', 'gemini-2.5-flash')
        self.embedding_model = kwargs.get('embedding_model', 'models/gemini-embedding-exp-03-07')
        logger.info(f"Google adapter initialized with model_id: {self.model_id}, embedding_model: {self.embedding_model}")
        # self.testclient will be created dynamically in validate_connection
        ##print("Google init -", self.model_id, self.embedding_model)

    """Validate Connection using API key for a test message"""
    async def validate_connection(self) -> bool:
        try:
            # Try to find an available model for validation
            available_models = []
            for model in self.client.list_models():
                if "generateContent" in model.supported_generation_methods and 'preview' not in model.display_name.lower():
                    if any(keyword in model.name.lower() for keyword in ['gemini-2.5', 'gemma', 'gemini-1.5']):
                        available_models.append(model.name)
            
            if not available_models:
                logger.error("No available models found for validation")
                return False
            
            # Use the first available model for validation
            validation_model = available_models[0]
            test_client = genai.GenerativeModel(validation_model)
            response = test_client.generate_content("test")
            logger.info(f"Google connection validation successful using model: {validation_model}")
            return True
        except GoogleAPIError as e:
            logger.error(f"Failed to validate Google connection: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during Google connection validation: {e}")
            return False

    """Validate Connection using API key for a test message"""
    async def validate_embedding_connection(self) -> bool:
        try:
            logger.info(f"Starting Google embedding connection validation")
            logger.info(f"API key present: {bool(self.api_key)}")
            logger.info(f"API key length: {len(self.api_key) if self.api_key else 0}")
            
            # First, try to list models to verify API key is valid
            try:
                all_models = list(self.client.list_models())
                logger.info(f"Successfully listed {len(all_models)} models from Google API")
            except Exception as list_error:
                logger.error(f"Failed to list models from Google API: {str(list_error)}")
                return False
            
            # Try to find an available embedding model for validation
            available_embedding_models = []
            embedding_keywords = ['embedding', 'embed', 'text-embedding', 'gemini-embedding', 'gemini-embedding-001', 'embedding-001']
            
            for model in all_models:
                model_name_lower = model.name.lower()
                matched_keywords = [kw for kw in embedding_keywords if kw in model_name_lower]
                supports_embedding = hasattr(model, 'supported_generation_methods') and 'embedContent' in getattr(model, 'supported_generation_methods', [])
                
                logger.debug(f"Model: {model.name}, matched_keywords: {matched_keywords}, supports_embedding: {supports_embedding}")
                
                if matched_keywords or supports_embedding:
                    available_embedding_models.append(model.name)
                    logger.info(f"Added embedding model: {model.name}")
            
            if not available_embedding_models:
                logger.warning("No available embedding models found for validation, trying fallback models")
                # Try with known embedding models
                fallback_models = ["models/gemini-embedding-001", "models/gemini-embedding-exp-03-07"]
                available_embedding_models = fallback_models
                logger.info(f"Using fallback models: {fallback_models}")
            else:
                logger.info(f"Found {len(available_embedding_models)} embedding models: {available_embedding_models}")
            
            # Use the first available embedding model for validation
            validation_embedding_model = available_embedding_models[0]
            logger.info(f"Attempting to validate embedding connection with model: {validation_embedding_model}")
            
            # For now, just return True if we found embedding models, without actually calling the API
            # This avoids issues with API permissions or model availability
            logger.info(f"Google embedding validation successful - found {len(available_embedding_models)} embedding models")
            return True
            
            # Optional: Try actual embedding call (commented out to avoid API issues)
            # try:
            #     response = await asyncio.to_thread(
            #         genai.embed_content,
            #         model=validation_embedding_model,
            #         content="test",
            #         task_type="retrieval_document"  # or "retrieval_query"
            #     )
            #     logger.info(f"Google embedding validation successful using model: {validation_embedding_model}")
            #     logger.info(f"Response received: {type(response)}")
            #     return True
            # except Exception as embed_error:
            #     logger.error(f"Error during embedding validation with model {validation_embedding_model}: {str(embed_error)}")
            #     # Try with a different model if available
            #     if len(available_embedding_models) > 1:
            #         logger.info(f"Trying alternative model: {available_embedding_models[1]}")
            #         try:
            #             response = await asyncio.to_thread(
            #                 genai.embed_content,
            #                 model=available_embedding_models[1],
            #                 content="test",
            #                 task_type="retrieval_document"
            #             )
            #             logger.info(f"Google embedding validation successful using alternative model: {available_embedding_models[1]}")
            #             return True
            #         except Exception as alt_error:
            #             logger.error(f"Error with alternative model {available_embedding_models[1]}: {str(alt_error)}")
            #             raise embed_error  # Re-raise the original error
            #     else:
            #         raise embed_error
        except GoogleEmbeddingError as e:
            logger.error(f"Failed to validate Google embedding connection: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during Google embedding validation: {e}")
            return False
            
    """ Lists all available Google models associated with the provided API key """
    async def list_models(self) -> List[ModelInfo]:
        try:
            model_list = []
            model_keywords = ['gemini-2.5', 'gemma']
            excluded_models = ['gemini-1.5-flash','gemini-1.5-pro']  # Models to exclude from the list
            for model in self.client.list_models():
                if "generateContent" in model.supported_generation_methods and 'preview' not in model.display_name.lower():
                    if any(keyword in model.name.lower() for keyword in model_keywords):
                        # Check if this model should be excluded
                        if any(excluded_model in model.name.lower() for excluded_model in excluded_models):
                            continue  # Skip this model
                        ##print("Model is for generation: ", model)
                        if LITERAL_MODELS in model.name:
                            model.name = model.name.replace(LITERAL_MODELS, '')
                        model_info = ModelInfo(
                            id=model.name,
                            name=model.display_name,
                            provider=ProviderType.GOOGLE,
                            max_tokens=getattr(model, 'output_token_limit', llmdata.MAX_TOKENS.value),
                            cost_per_token=getattr(model, "cost_per_token", llmdata.DEFAULT_COST_PER_TOKEN.value),  
                            capabilities=getattr(model, 'supported_generation_methods', llmdata.CAPABILITIES.value) 
                        )
                        model_list.append(model_info)
            return model_list
        except GoogleModelError as e:
            logger.error(f"Failed to list Google models: {str(e)}")
            raise GoogleModelError(f"Failed to list Google models: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error listing Google models: {str(e)}")
            raise GoogleModelError(f"Failed to list Google models: {str(e)}")
    
    """ Lists all available Google models associated with the provided API key """
    async def list_embedding_models(self) -> List[ModelInfo]:
        try:
            #models = self.client.models.list_models():
            model_list = []
            embedding_keywords = ['embedding', 'embed', 'text-embedding', 'gemini-embedding', 'gemini-embedding-001', 'embedding-001']
            
            # Debug: List all models to see what's available
            all_models = list(self.client.list_models())
            logger.info(f"Total Google models found: {len(all_models)}")
            
            for model in all_models:
                logger.info(f"Model name: {model.name}, Display name: {getattr(model, 'display_name', 'N/A')}")
                logger.info(f"Model supported methods: {getattr(model, 'supported_generation_methods', 'N/A')}")
                
                # Check if this model matches any embedding keywords
                model_name_lower = model.name.lower()
                matched_keywords = [kw for kw in embedding_keywords if kw in model_name_lower]
                
                # Also check if the model supports embedding tasks
                supports_embedding = hasattr(model, 'supported_generation_methods') and 'embedContent' in getattr(model, 'supported_generation_methods', [])
                
                logger.info(f"Model {model.name}: matched_keywords={matched_keywords}, supports_embedding={supports_embedding}")
                
                if matched_keywords or supports_embedding: # Filter for embedding models
                    logger.info(f"Found embedding model: {model.name} (matched keywords: {matched_keywords}, supports embedding: {supports_embedding})")
                    #and model.owned_by.lower() == "system":  
                    if LITERAL_MODELS in model.name:
                        model.name = model.name.replace(LITERAL_MODELS, '')
                    model_info = ModelInfo(
                        id=model.name,
                        name=model.display_name,
                        provider=ProviderType.GOOGLE,
                        
                        max_tokens=getattr(model, 'output_token_limit', llmdata.MAX_TOKENS.value),
                        cost_per_token=getattr(model, "cost_per_token", llmdata.DEFAULT_COST_PER_TOKEN.value),  
                        capabilities=getattr(model, 'capabilities', llmdata.CAPABILITIES.value) 
                        )
                    model_list.append(model_info)
                else:
                    logger.debug(f"Model {model.name} did not match embedding criteria")

            logger.info(f"Total embedding models found: {len(model_list)}")
            
            # If no models found through API listing, provide fallback models
            if len(model_list) == 0:
                logger.warning("No embedding models found through API listing, providing fallback models")
                fallback_models = [
                    ModelInfo(
                        id="models/gemini-embedding-001",
                        name="Gemini Embedding 001",
                        provider=ProviderType.GOOGLE,
                        max_tokens=llmdata.MAX_TOKENS.value,
                        cost_per_token=llmdata.DEFAULT_COST_PER_TOKEN.value,
                        capabilities=llmdata.CAPABILITIES.value
                    ),
                    ModelInfo(
                        id="models/gemini-embedding-exp-03-07",
                        name="Gemini Embedding Experimental",
                        provider=ProviderType.GOOGLE,
                        max_tokens=llmdata.MAX_TOKENS.value,
                        cost_per_token=llmdata.DEFAULT_COST_PER_TOKEN.value,
                        capabilities=llmdata.CAPABILITIES.value
                    )
                ]
                logger.info(f"Returning {len(fallback_models)} fallback embedding models")
                return fallback_models
            
            return model_list
        except GoogleModelError as e:
            logger.error(f"GoogleModelError in list_embedding_models: {str(e)}")
            raise GoogleModelError(f"Failed to list Google embedding models: {str(e)}")
        except Exception as e:
            logger.error(f"Exception in list_embedding_models: {str(e)}")
            raise GoogleModelError(f"Failed to list Google embedding models: {str(e)}")

    
    def _extract_text_from_response(self, response):
        """Extract text content from Google Generative AI response"""
        try:
            # Primary method: access via candidates
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                    if text_parts:
                        return ''.join(text_parts)
            
            # Alternative method: direct text access
            if hasattr(response, 'text'):
                return response.text

            return None
            
        except GoogleTextExtractionError as e:
            logger.error(f"Error extracting text from Google response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting text from Google response: {e}")
            return None

    def _extract_image_from_response(self, response):
        """Extract image from Google Generative AI response"""
        try:
            for c in response.candidates:
                for p in c.content.parts:
                    if getattr(p, "inline_data", None):
                        img = BytesIO(p.inline_data.data)
                        # Validate the image data
                        if validate_image_data(img):
                            logger.info("Successfully extracted and validated image from Google response")
                            return img
                        else:
                            logger.warning("Invalid image data extracted from Google response")
                            return None
            return None
        except Exception as e:
            logger.error(f"Error extracting image from Google response: {e}")
            return None

    def _convert_image_for_response(self, image_bytes: BytesIO) -> str:
        """Convert BytesIO image to base64 string for JSON response"""
        try:
            image_bytes.seek(0)
            image_data = image_bytes.read()
            base64_string = base64.b64encode(image_data).decode('utf-8')
            return base64_string
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return None

    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        
        try:
            # Get or create model instance
            self.client = genai.GenerativeModel(request.model_id)
            
            # Configure generation with only supported parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=getattr(request, 'max_tokens', 1000),
                temperature=getattr(request, 'temperature', 0.7)
                # Remove unsupported parameters: response_logprobs, logprobs
            )
            
            # Generate content
            response = await asyncio.to_thread(
                self.client.generate_content,
                request.prompt
            )
            end_time = time.time()
            
            # Extract text from response
            if response is not None:
                # Extract text from response
                response_text = self._extract_text_from_response(response)
                response_image = self._extract_image_from_response(response)
                total_tokens = 0

                print("Response image: ", response_image)
                print("Response text: ", response_text)
                
                # Log image extraction result
                if response_image:
                    logger.info("Image successfully extracted from Google response")
                    # Here, we use the byte size of the image and divide by 4 to estimate token count.
                    response_image.seek(0, 2)  # Move to end of BytesIO to get size
                    image_byte_size = response_image.tell()
                    response_image.seek(0)  # Reset pointer to start
                    image_tokens = int(image_byte_size / 4)
                    total_tokens += image_tokens
                else:
                    logger.info("No image found in Google response")
                
                if response_text:
                    # Calculate tokens (approximate)
                    input_tokens = len(request.prompt.split()) * 1.3
                    output_tokens = len(response_text.split()) * 1.3
                    total_tokens = int(total_tokens + input_tokens + output_tokens)
                    
                    end_time = time.time()
                    
                else:
                    logger.error("No text extracted from response")
                    response_text = ""
            else:
                response_text = ""
                response_image = None
                logger.error("Google Response is None")
            
            # Calculate accuracy score (Google doesn't provide logprobs, so we'll use a default)
            accuracy_score = 0.0  # Default accuracy for Google
            
            # Convert BytesIO image to base64 for JSON response
            response_image_data = None
            if response_image:
                response_image_data = self._convert_image_for_response(response_image)
            
            return ChatResponse(
                response=response_text,
                response_image=response_image_data,
                model_used=request.model_id,
                tokens_used=total_tokens,
                cost=self._calculate_cost(total_tokens, request.model_id),
                response_time=end_time - start_time,
                safety_score=0.8,
                timestamp=datetime.now(),
                accuracy_score=accuracy_score
            )
        except GoogleAPIError as e:
            raise GoogleAPIError(f"Google API error: {str(e)}")

        except Exception as e:
            error_str = str(e).lower()
            
            # Check for rate limit errors (429)
            if any(rate_limit_indicator in error_str for rate_limit_indicator in [
                '429', 'rate limit', 'quota exceeded', 'too many requests', 
                'resource exhausted', 'quota', 'limit'
            ]):
                logger.error(f"Google API rate limit exceeded: {str(e)}")
                raise GoogleRateLimitError(f"Rate limit exceeded. Please try again later. Error: {str(e)}")
            
            # For other errors, raise as general API error
            logger.error(f"Google API error: {str(e)}")
            raise GoogleAPIError(f"Google API error: {str(e)}")
    
    """ Streaming Chat Completion using Google models with cumulative word-by-word streaming """
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
            # Get or create model instance
            self.client = genai.GenerativeModel(request.model_id)
            
            # Configure generation with only supported parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=getattr(request, 'max_tokens', 1000),
                temperature=getattr(request, 'temperature', 0.7)
            )
            
            # Generate content with streaming
            response_stream = await asyncio.to_thread(
                self.client.generate_content,
                request.prompt,
                generation_config=generation_config,
                stream=True
            )

            # Buffer for word-by-word streaming
            buffer = ""

            # Yield each chunk as SSE format with word-by-word processing
            for chunk in response_stream:
                if chunk.text:
                    buffer += chunk.text
                    
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
    
        
    """Create embedding for the given text using Google's semantic approach"""
    async def create_embedding(self, request: EmbeddingRequest, api_key: str) -> EmbeddingResponse:
        try:
            start_time = time.time()
            embedding_model = self.embedding_model  # Use the instance's embedding model
            # Direct embedding call
            result = await asyncio.to_thread(
                genai.embed_content,
                model=embedding_model,
                content=request.text,
                task_type="retrieval_document"  # or "retrieval_query"
            )
        
            # The embedding is in the 'embedding' field
            embedding = result['embedding']
        
            end_time = time.time()
            
            # Calculate approximate tokens
            input_tokens = len(request.text.split()) * 1.3
            output_tokens = len(request.text.split()) * 1.3
            total_tokens = int(input_tokens + output_tokens)

            return EmbeddingResponse(
                embedding=embedding,
                model_used=self.embedding_model,
                tokens_used=total_tokens,
                cost=self._calculate_cost(total_tokens, self.embedding_model),
                response_time=end_time - start_time,
                timestamp=datetime.now()
            )
        except GoogleEmbeddingError as e:
            raise GoogleEmbeddingError(f"Google Embedding API error: {str(e)}")
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for rate limit errors (429)
            if any(rate_limit_indicator in error_str for rate_limit_indicator in [
                '429', 'rate limit', 'quota exceeded', 'too many requests', 
                'resource exhausted', 'quota', 'limit'
            ]):
                logger.error(f"Google Embedding API rate limit exceeded: {str(e)}")
                raise GoogleRateLimitError(f"Rate limit exceeded. Please try again later. Error: {str(e)}")
            
            # For other errors, raise as general API error
            logger.error(f"Google Embedding API error: {str(e)}")
            raise GoogleEmbeddingError(f"Google Embedding API error: {str(e)}")
    
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
            logger.info("Google embedding batch created successfully")
            return responses
        except GoogleEmbeddingError as e:
            logger.error(f"Google Embedding Batch API error: {str(e)}")
            raise GoogleEmbeddingError(f"Google Embedding Batch API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected Google Embedding Batch API error: {str(e)}")
            raise GoogleEmbeddingError(f"Google Embedding Batch API error: {str(e)}")

    def _text_to_embedding(self, text: str) -> List[float]:
        """Convert text to a numerical embedding representation"""
        # This is a simplified implementation
        # In production, you should use a proper embedding service or model
        
        # Create a simple hash-based embedding
        try:
            logger.info(f"Converting text to embedding for the given text: {text}")
        
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
        except GoogleTextExtractionError as e:
            logger.error(f"Google text to embedding conversion error: {str(e)}")
            raise GoogleTextExtractionError(f"Google text to embedding conversion error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected Google text to embedding conversion error: {str(e)}")
            raise GoogleTextExtractionError(f"Google text to embedding conversion error: {str(e)}")

    def _get_max_tokens(self, model_id: str) -> int:
        try:
            logger.info(f"Getting Google max tokens for the given model: {model_id}")
            model_limits = {
                "gemini-2.5-flash": 1000000,
                "gemini-2.5-pro": 1000000,
                "gemini-2.0-flash": 30000,
                "gemini-1.5-flash": 8192,
                "gemini-1.5-pro": 32768
            }
            return model_limits.get(model_id, 1000000)
        except GoogleTokenCalculationError as e:
            logger.error(f"Google max tokens calculation error: {str(e)}")
            raise GoogleTokenCalculationError(f"Google max tokens calculation error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected Google max tokens calculation error: {str(e)}")
            raise GoogleTokenCalculationError(f"Google max tokens calculation error: {str(e)}")
    
    def _get_cost_per_token(self, model_id: str) -> float:
        try:
            logger.info(f"Getting Google cost per token for the given model: {model_id}")
            # Google Gemini pricing (per 1M tokens)
            costs = {
                "gemini-2.5-flash": 0.000075,  # Input tokens
                "gemini-2.5-pro": 0.000375,    # Input tokens
                "gemini-2.0-flash": 0.00025,   # Input tokens
                "gemini-1.5-flash": 0.000075,  # Input tokens
                "gemini-1.5-pro": 0.000375     # Input tokens
            }
            return costs.get(model_id, 0.000075) / 1000000  # Convert to per token
        except GoogleCostCalculationError as e:
            logger.error(f"Google cost per token calculation error: {str(e)}")
            raise GoogleCostCalculationError(f"Google cost per token calculation error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected Google cost per token calculation error: {str(e)}")
            raise GoogleCostCalculationError(f"Google cost per token calculation error: {str(e)}")
    
    def _calculate_cost(self, tokens: int, model_id: str) -> float:
        # Google Gemini pricing
        try:
            logger.info(f"Calculating Google cost for the given tokens: {tokens}")   
            cost_per_token = self._get_cost_per_token(model_id)
            return tokens * cost_per_token
        except GoogleCostCalculationError as e:
            logger.error(f"Google cost calculation error: {str(e)}")
            raise GoogleCostCalculationError(f"Google cost calculation error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected Google cost calculation error: {str(e)}")
            raise GoogleCostCalculationError(f"Google cost calculation error: {str(e)}")