"""Base provider interface for all LLM providers."""

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, List
from .settings import GenerationRequest, GenerationResponse, StreamChunk, ProviderInfo
from .utils.config import ProviderConfig
from .utils.logger import logger


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    def __init__(self, config: Optional[ProviderConfig] = None) -> None:
        """Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self._is_initialized = False
        self.provider_name = self.__class__.__name__.lower().replace("provider", "")
    
    @abstractmethod
    def get_provider_info(self) -> ProviderInfo:
        """Get information about this provider.
        
        Returns:
            ProviderInfo object with provider details
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider (setup client, validate config, etc.).
        
        Raises:
            InvalidConfigurationError: If configuration is invalid
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text based on the request.
        
        Args:
            request: Generation request with prompt and parameters
            
        Returns:
            GenerationResponse with generated content
            
        Raises:
            APIError: If API call fails
            ModelNotAvailableError: If model is not available
            GenerationError: If generation fails
        """
        pass
    
    @abstractmethod
    async def stream_generate(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        """Generate text with streaming response.
        
        Args:
            request: Generation request with prompt and parameters
            
        Yields:
            StreamChunk objects with partial content
            
        Raises:
            APIError: If API call fails
            ModelNotAvailableError: If model is not available
            GenerationError: If generation fails
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Get list of supported models for this provider.
        
        Returns:
            List of model names
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the provider configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            InvalidConfigurationError: If configuration is invalid
        """
        pass
    
    async def ensure_initialized(self) -> None:
        """Ensure the provider is initialized."""
        if not self._is_initialized:
            await self.initialize()
            self._is_initialized = True
            logger.info(f"Provider initialized successfully", self.provider_name)
    
    def is_model_supported(self, model: str) -> bool:
        """Check if a model is supported by this provider.
        
        Args:
            model: Model name to check
            
        Returns:
            True if model is supported
        """
        return model in self.get_supported_models()
    
    def __str__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}(model={getattr(self.config, 'model', 'unknown')})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the provider."""
        return (
            f"{self.__class__.__name__}("
            f"config={self.config}, "
            f"initialized={self._is_initialized})"
        )