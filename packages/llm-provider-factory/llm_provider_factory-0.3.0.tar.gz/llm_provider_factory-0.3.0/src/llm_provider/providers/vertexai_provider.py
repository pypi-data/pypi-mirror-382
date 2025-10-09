"""Google Cloud Vertex AI provider implementation."""

from typing import Optional, AsyncIterator, List, Dict, Any
import os
import httpx
import asyncio

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
    from google.cloud import aiplatform
    from vertexai.generative_models import GenerativeModel
    import vertexai
    import google.auth
    from google.auth.transport.requests import Request
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False
    logger.warning("⚠️ google-cloud-aiplatform paketi yüklü değil. Vertex AI provider devre dışı.")


class VertexAIProvider(BaseLLMProvider):
    """Google Cloud Vertex AI LLM sağlayıcısı (Gemini ve Mistral modelleri)"""
    
    SUPPORTED_MODELS = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.0-pro", 
        "text-bison",
        "text-bison-32k",
        "chat-bison",
        "chat-bison-32k",
        "mistral-large-2411",
        "mistral-7b-instruct"
    ]
    
    def __init__(self, config: Optional[VertexAIConfig] = None) -> None:
        """Initialize Vertex AI provider.
        
        Args:
            config: Vertex AI configuration. If None, will try to load from environment.
        """
        if config is None:
            config = VertexAIConfig.from_env()
        
        super().__init__(config)
        self.config: VertexAIConfig = config
        self.project_id = config.project_id
        self.location = config.location
        self.model_name = config.model
        self.temperature = config.temperature
        self.max_output_tokens = config.max_tokens
        self.model = None
        
        # Set credentials if provided
        if config.credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.credentials_path
        
        logger.info(f"🔧 VertexAI Provider oluşturuldu: model={self.model_name}, project={self.project_id}")
    
    async def initialize(self) -> None:
        """Initialize Vertex AI client."""
        if not VERTEXAI_AVAILABLE:
            raise InvalidConfigurationError("google-cloud-aiplatform package not installed", "vertexai")
        
        if not self.project_id:
            raise InvalidConfigurationError("Google Cloud Project ID is required", "vertexai")
        
        try:
            # Vertex AI'yi initialize et
            vertexai.init(project=self.project_id, location=self.location)
            
            # Model'i oluştur - Mistral modelleri için özel handling
            if "mistral" in self.model_name.lower():
                # Mistral modelleri için farklı yaklaşım deneyebiliriz
                try:
                    self.model = GenerativeModel(self.model_name)
                    logger.info(f"✅ Mistral model başlatıldı: {self.model_name}")
                except Exception as mistral_error:
                    logger.warning(f"⚠️ Mistral model doğrudan başlatılamadı: {mistral_error}")
                    # Fallback: Gemini kullan
                    self.model_name = "gemini-1.5-flash"
                    self.model = GenerativeModel(self.model_name)
                    logger.info(f"🔄 Fallback olarak Gemini kullanılıyor: {self.model_name}")
            else:
                # Normal Gemini modelleri için
                self.model = GenerativeModel(self.model_name)
                logger.info(f"✅ Vertex AI provider başlatıldı: {self.project_id}, model: {self.model_name}")
            
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
            logger.warning(f"Model '{self.config.model}' might not be fully supported. Supported models: {', '.join(self.SUPPORTED_MODELS)}")
        
        # Check credentials
        if not self.config.credentials_path and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            raise InvalidConfigurationError(
                "Google Cloud credentials are required. Set GOOGLE_APPLICATION_CREDENTIALS or provide credentials_path", 
                "vertexai"
            )
        
        return True
    
    def is_available(self) -> bool:
        """Sağlayıcı kullanılabilir mi?"""
        return VERTEXAI_AVAILABLE and self.model_name is not None and self.project_id is not None
    
    def _get_credentials_token(self) -> str:
        """Get Google Cloud access token."""
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        return credentials.token
    
    def _build_mistral_endpoint_url(self, model_name: str, streaming: bool = False) -> str:
        """Build Mistral endpoint URL for rawPredict API."""
        base_url = f"https://{self.location}-aiplatform.googleapis.com/v1/"
        project_fragment = f"projects/{self.project_id}"
        location_fragment = f"locations/{self.location}"
        specifier = "streamRawPredict" if streaming else "rawPredict"
        model_fragment = f"publishers/mistralai/models/{model_name}"
        url = f"{base_url}{'/'.join([project_fragment, location_fragment, model_fragment])}:{specifier}"
        return url
    
    async def _generate_mistral_response(self, messages: List[Dict], streaming: bool = False) -> str:
        """Generate response using Mistral rawPredict API."""
        try:
            # Get access token
            access_token = self._get_credentials_token()
            
            # Build URL
            url = self._build_mistral_endpoint_url(self.model_name, streaming)
            
            # Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }
            
            # Payload
            data = {
                "model": self.model_name,
                "messages": messages,
                "stream": streaming,
                "temperature": self.temperature,
                "max_tokens": self.max_output_tokens
            }
            
            # Make request
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=data, headers=headers, timeout=30.0)
                resp.raise_for_status()
                
                result = resp.json()
                
                # Extract response text
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise ValueError("No response content from Mistral API")
                    
        except Exception as e:
            logger.error(f"❌ Mistral API error: {e}")
            raise GenerationError(f"Mistral API error: {str(e)}", "vertexai")
    
    async def generate_response(self, text: str, system_prompt: str = None, history: List[Dict] = None) -> str:
        """Vertex AI ile cevap oluştur (history destekli) - Sizin formatınızda"""
        try:
            await self.ensure_initialized()
            
            # Mistral modelleri için özel API kullan
            if "mistral" in self.model_name.lower():
                messages = []
                
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                
                if history:
                    for msg in history:
                        messages.append({
                            "role": msg.get("role", "user"), 
                            "content": msg.get("content", "")
                        })
                
                messages.append({"role": "user", "content": text})
                
                return await self._generate_mistral_response(messages)
            
            # Gemini modelleri için normal yöntem
            if not self.model:
                raise ValueError("Vertex AI model başlatılamadı")
            
            # System prompt hazırla
            if not system_prompt:
                system_prompt = "Sen yardımcı bir asistansın. Kısa ve anlaşılır cevaplar ver."
            
            # Prompt'u hazırla
            if history:
                # History varsa, chat formatında birleştir
                conversation = f"{system_prompt}\n\n"
                for msg in history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        conversation += f"Kullanıcı: {content}\n"
                    else:
                        conversation += f"Asistan: {content}\n"
                conversation += f"Kullanıcı: {text}\nAsistan:"
            else:
                conversation = f"{system_prompt}\n\nKullanıcı: {text}\nAsistan:"
            
            logger.info(f"Vertex AI'ya gönderilen prompt: {conversation[:100]}...")
            
            # Vertex AI'ye istek gönder
            response = self.model.generate_content(
                conversation,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_output_tokens
                }
            )
            
            # Cevabı al
            if response and response.text:
                answer = response.text.strip()
                logger.info(f"✅ Vertex AI cevabı alındı: {len(answer)} karakter")
                return answer
            else:
                logger.warning("⚠️ Vertex AI boş cevap döndü")
                return "Üzgünüm, şu anda bir cevap üretemedim."
                
        except Exception as e:
            logger.error(f"❌ Vertex AI LLM hatası: {e}")
            raise GenerationError(f"Vertex AI error: {str(e)}", "vertexai")
    
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate response using Vertex AI."""
        try:
            await self.ensure_initialized()
            
            # Convert messages to conversation format
            conversation_history = []
            system_prompt = "Sen yardımcı bir asistansın."
            
            # Handle prompt or messages
            if request.prompt:
                # If prompt is provided, use it directly
                text = request.prompt
            elif request.messages:
                # Handle messages if present
                for msg in request.messages:
                    # Handle role - could be string or enum
                    role_value = msg.role.value if hasattr(msg.role, 'value') else str(msg.role)
                    
                    if role_value == "system":
                        system_prompt = msg.content
                    else:
                        conversation_history.append({
                            "role": role_value,
                            "content": msg.content
                        })
                
                # Get the last user message
                text = conversation_history[-1]["content"] if conversation_history else ""
            else:
                raise GenerationError("Either prompt or messages must be provided", "vertexai")
            
            # Generate response
            response_text = await self.generate_response(
                text=text,
                system_prompt=system_prompt,
                history=conversation_history[:-1] if conversation_history else []
            )
            
            return GenerationResponse(
                content=response_text,
                model=self.model_name,
                usage={"total_tokens": len(response_text.split())}  # Approximate token count
            )
            
        except Exception as e:
            logger.error(f"❌ Vertex AI generation error: {e}")
            raise GenerationError(f"Vertex AI generation failed: {str(e)}", "vertexai")
    
    async def stream_generate(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        """Stream generate response using Vertex AI."""
        try:
            # Vertex AI doesn't support streaming in this simple implementation
            # So we'll generate the full response and yield it in chunks
            response = await self.generate(request)
            
            # Split response into chunks
            words = response.content.split()
            chunk_size = 5  # Words per chunk
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)
                
                yield StreamChunk(
                    content=chunk_text + (" " if i + chunk_size < len(words) else ""),
                    model=self.model_name,
                    finish_reason="partial" if i + chunk_size < len(words) else "complete"
                )
                
        except Exception as e:
            logger.error(f"❌ Vertex AI stream generation error: {e}")
            raise GenerationError(f"Vertex AI stream generation failed: {str(e)}", "vertexai")
    
    def get_provider_info(self) -> ProviderInfo:
        """Get provider information."""
        return ProviderInfo(
            name="vertexai",
            display_name="Google Cloud Vertex AI",
            description="Google Cloud Vertex AI provider supporting Gemini and Mistral models",
            supported_models=self.SUPPORTED_MODELS,
            capabilities=["text_generation", "conversation", "streaming", "system_messages"],
            is_available=self.is_available()
        )