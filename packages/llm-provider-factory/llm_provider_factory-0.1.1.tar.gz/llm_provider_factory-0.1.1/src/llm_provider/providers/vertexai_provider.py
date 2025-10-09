"""Google Cloud Vertex AI provider implementation."""

from typing import Optional, AsyncIterator, List, Dict, Any
import os

from ..base_provider import BaseLLMProvider
from ..settings import (
    GenerationRequest, 
    GenerationResponse, 
    StreamChunk, 
    ProviderInfo,
    Message,
    MessageRole
)
from ..utils.config import ProviderConfig, VertexAIConfig
from ..utils.exceptions import (
    InvalidConfigurationError,
    AuthenticationError,
    APIError,
    RateLimitError,
    ModelNotAvailableError,
    GenerationError
)
from ..utils.logger import logger

# Import Vertex AI with proper error handling
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False
    logger.warning("⚠️ google-cloud-aiplatform paketi yüklü değil. Vertex AI provider devre dışı.")


class VertexAIProvider(BaseLLMProvider):
    """Google Cloud Vertex AI LLM provider implementation."""
    
    SUPPORTED_MODELS = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.0-pro",
        "text-bison",
        "text-bison-32k",
        "chat-bison",
        "chat-bison-32k"
    ]
    
    def __init__(self, config: Optional[VertexAIConfig] = None) -> None:
        """Initialize Vertex AI provider.
        
        Args:
            config: Vertex AI configuration. If None, will try to load from environment.
        """
        if config is None:
            config = VertexAIConfig.from_env()
        
        super().__init__(config)
        self.model: Optional[GenerativeModel] = None
        self.config: VertexAIConfig = config
    
    def get_provider_info(self) -> ProviderInfo:
        """Get Vertex AI provider information."""
        return ProviderInfo(
            name="vertexai",
            display_name="Google Cloud Vertex AI",
            description="Google Cloud Vertex AI models including Gemini and PaLM",
            supported_models=self.SUPPORTED_MODELS,
            capabilities=["chat", "completion", "streaming"],
            is_available=self._check_availability()
        )
    
    def _check_availability(self) -> bool:
        """Check if Vertex AI is available."""
        if not VERTEXAI_AVAILABLE:
            return False
        
        # Check if we have required configuration
        return (self.config.project_id is not None and 
                (self.config.credentials_path is not None or 
                 os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is not None))
    
    async def initialize(self) -> None:
        """Initialize Vertex AI client."""
        if not self.validate_config():
            raise InvalidConfigurationError("Invalid Vertex AI configuration", "vertexai")
        
        if not VERTEXAI_AVAILABLE:
            raise InvalidConfigurationError("google-cloud-aiplatform package not installed", "vertexai")
        
        try:
            # Set credentials if provided
            if self.config.credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.config.credentials_path
            
            # Initialize Vertex AI
            vertexai.init(
                project=self.config.project_id,
                location=self.config.location
            )
            
            # Create the model
            self.model = GenerativeModel(self.config.model)
            
            logger.info(f"Vertex AI client initialized successfully with project: {self.config.project_id}", "vertexai")
            
        except Exception as e:
            if "authentication" in str(e).lower() or "credentials" in str(e).lower():
                raise AuthenticationError(f"Vertex AI authentication failed: {str(e)}", "vertexai")
            else:
                raise APIError(f"Failed to initialize Vertex AI client: {str(e)}", "vertexai")
    
    def validate_config(self) -> bool:
        """Validate Vertex AI configuration."""
        if not self.config.project_id:
            raise InvalidConfigurationError("Google Cloud Project ID is required", "vertexai")
        
        if self.config.model not in self.SUPPORTED_MODELS:
            raise InvalidConfigurationError(
                f"Model '{self.config.model}' is not supported. "
                f"Supported models: {', '.join(self.SUPPORTED_MODELS)}", 
                "vertexai"
            )
        
        # Check credentials
        if not self.config.credentials_path and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            raise InvalidConfigurationError(
                "Google Cloud credentials are required. Set GOOGLE_APPLICATION_CREDENTIALS or provide credentials_path", 
                "vertexai"
            )
        
        return True
    
    def get_supported_models(self) -> List[str]:
        """Get supported Vertex AI models."""
        return self.SUPPORTED_MODELS.copy()
    
    def _convert_messages(self, request: GenerationRequest) -> str:
        """Convert request to Vertex AI format."""
        conversation_parts = []
        
        # Process conversation history
        if request.history:
            for msg in request.history:
                if msg.role == MessageRole.SYSTEM:
                    # System messages go at the beginning
                    conversation_parts.insert(0, f"System: {msg.content}\n")
                elif msg.role == MessageRole.USER:
                    conversation_parts.append(f"User: {msg.content}\n")
                elif msg.role == MessageRole.ASSISTANT:
                    conversation_parts.append(f"Assistant: {msg.content}\n")
        
        # Add current prompt
        conversation_parts.append(f"User: {request.prompt}\n")
        conversation_parts.append("Assistant:")
        
        return "".join(conversation_parts)
    
    def _parse_finish_reason(self, finish_reason: Optional[str]) -> Optional[str]:
        """Parse Vertex AI finish reason."""
        if not finish_reason:
            return None
        
        reason_map = {
            "STOP": "stop",
            "MAX_TOKENS": "max_tokens",
            "SAFETY": "safety",
            "RECITATION": "recitation",
            "OTHER": "other"
        }
        
        return reason_map.get(finish_reason, finish_reason.lower())
    
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using Vertex AI API."""
        await self.ensure_initialized()
        
        try:
            # Prepare the prompt
            prompt = self._convert_messages(request)
            
            # Create generation config
            generation_config = {
                "temperature": request.temperature or self.config.temperature,
                "max_output_tokens": request.max_tokens or self.config.max_tokens,
            }
            
            if request.top_p is not None:
                generation_config["top_p"] = request.top_p
            
            if request.stop_sequences:
                generation_config["stop_sequences"] = request.stop_sequences
            
            logger.debug(f"Making Vertex AI API call with model: {self.config.model}", "vertexai")
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract content
            content = response.text if response.text else ""
            
            # Get usage information if available
            usage = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count,
                }
            
            # Get finish reason
            finish_reason = None
            if response.candidates and response.candidates[0].finish_reason:
                finish_reason = self._parse_finish_reason(response.candidates[0].finish_reason.name)
            
            return GenerationResponse(
                content=content,
                finish_reason=finish_reason,
                usage=usage,
                provider="vertexai",
                model=self.config.model,
                metadata={
                    "project_id": self.config.project_id,
                    "location": self.config.location,
                    "safety_ratings": [
                        {
                            "category": rating.category.name,
                            "probability": rating.probability.name
                        }
                        for rating in (response.candidates[0].safety_ratings if response.candidates else [])
                    ]
                }
            )
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "quota" in error_msg or "rate" in error_msg:
                raise RateLimitError(f"Vertex AI rate limit exceeded: {str(e)}", "vertexai")
            elif "authentication" in error_msg or "permission" in error_msg:
                raise AuthenticationError(f"Vertex AI authentication error: {str(e)}", "vertexai")
            elif "model" in error_msg and "not found" in error_msg:
                raise ModelNotAvailableError(f"Vertex AI model not found: {str(e)}", self.config.model, "vertexai")
            else:
                raise GenerationError(f"Vertex AI generation failed: {str(e)}", "vertexai")
    
    async def stream_generate(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        """Generate text with streaming using Vertex AI API."""
        await self.ensure_initialized()
        
        try:
            # Prepare the prompt
            prompt = self._convert_messages(request)
            
            # Create generation config
            generation_config = {
                "temperature": request.temperature or self.config.temperature,
                "max_output_tokens": request.max_tokens or self.config.max_tokens,
            }
            
            if request.top_p is not None:
                generation_config["top_p"] = request.top_p
            
            if request.stop_sequences:
                generation_config["stop_sequences"] = request.stop_sequences
            
            logger.debug(f"Starting Vertex AI streaming with model: {self.config.model}", "vertexai")
            
            # Generate content with streaming
            response_stream = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response_stream:
                if chunk.text:
                    yield StreamChunk(
                        content=chunk.text,
                        is_final=False,
                        metadata={
                            "safety_ratings": [
                                {
                                    "category": rating.category.name,
                                    "probability": rating.probability.name
                                }
                                for rating in (chunk.candidates[0].safety_ratings if chunk.candidates else [])
                            ]
                        }
                    )
            
            # Send final chunk
            yield StreamChunk(
                content="",
                is_final=True,
                finish_reason="stop"
            )
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "quota" in error_msg or "rate" in error_msg:
                raise RateLimitError(f"Vertex AI rate limit exceeded: {str(e)}", "vertexai")
            elif "authentication" in error_msg or "permission" in error_msg:
                raise AuthenticationError(f"Vertex AI authentication error: {str(e)}", "vertexai")
            elif "model" in error_msg and "not found" in error_msg:
                raise ModelNotAvailableError(f"Vertex AI model not found: {str(e)}", self.config.model, "vertexai")
            else:
                raise GenerationError(f"Vertex AI streaming failed: {str(e)}", "vertexai")