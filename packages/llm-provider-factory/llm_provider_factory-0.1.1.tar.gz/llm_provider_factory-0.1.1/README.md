# LLM Provider Factory

A unified, extensible Python library for interacting with multiple Large Language Model (LLM) providers through a single, consistent interface. Support for OpenAI, Anthropic Claude, Google Gemini, and easy extension for new providers.

## 🌟 Features

- **Unified Interface**: Single API for multiple LLM providers
- **Async Support**: Full async/await support for better performance
- **Streaming**: Real-time streaming responses from all providers
- **Type Safety**: Complete type hints and Pydantic models
- **Error Handling**: Comprehensive error handling with specific exceptions
- **Configuration Management**: Flexible configuration system
- **Extensible**: Easy to add new providers
- **Testing**: Full test coverage with mocking support

## 🚀 Quick Start

### Installation

```bash
pip install llm-provider-factory
```

### Basic Usage

```python
import asyncio
from llm_provider import LLMProviderFactory, OpenAI, OpenAIConfig

async def main():
    # Method 1: Direct provider instantiation
    provider = LLMProviderFactory(OpenAI())
    response = await provider.generate("Hello, world!")
    print(response.content)
    
    # Method 2: Using factory with configuration
    config = OpenAIConfig(api_key="your-api-key", model="gpt-4")
    factory = LLMProviderFactory.create_openai(config)
    response = await factory.generate("Tell me a joke")
    print(response.content)

asyncio.run(main())
```

## 📖 Detailed Usage

### Configuration

#### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"  
export GOOGLE_API_KEY="your-google-key"
```

#### Programmatic Configuration
```python
from llm_provider import OpenAIConfig, AnthropicConfig, GeminiConfig

# OpenAI Configuration
openai_config = OpenAIConfig(
    api_key="your-key",
    model="gpt-4",
    max_tokens=1000,
    temperature=0.7
)

# Anthropic Configuration
anthropic_config = AnthropicConfig(
    api_key="your-key",
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    temperature=0.7
)

# Gemini Configuration
gemini_config = GeminiConfig(
    api_key="your-key",
    model="gemini-pro",
    max_tokens=1000,
    temperature=0.7
)
```

### Multiple Provider Usage

```python
from llm_provider import LLMProviderFactory

async def compare_providers():
    factory = LLMProviderFactory()
    prompt = "Explain quantum computing in simple terms"
    
    # Generate with different providers
    openai_response = await factory.generate(prompt, provider="openai")
    anthropic_response = await factory.generate(prompt, provider="anthropic")
    gemini_response = await factory.generate(prompt, provider="gemini")
    
    print(f"OpenAI: {openai_response.content}")
    print(f"Anthropic: {anthropic_response.content}")
    print(f"Gemini: {gemini_response.content}")
```

### Conversation History

```python
from llm_provider import Message, MessageRole

async def conversation_example():
    factory = LLMProviderFactory.create_openai()
    
    history = [
        Message(role=MessageRole.USER, content="Hello, I'm learning Python"),
        Message(role=MessageRole.ASSISTANT, content="Hello! I'd be happy to help you learn Python."),
        Message(role=MessageRole.USER, content="Can you explain variables?")
    ]
    
    response = await factory.generate(
        "Now explain functions",
        history=history
    )
    print(response.content)
```

### Streaming Responses

```python
async def streaming_example():
    factory = LLMProviderFactory.create_openai()
    
    async for chunk in factory.stream_generate("Write a short story about AI"):
        if chunk.content:
            print(chunk.content, end="", flush=True)
        
        if chunk.is_final:
            print(f"\nFinish reason: {chunk.finish_reason}")
            break
```

### Error Handling

```python
from llm_provider import (
    AuthenticationError,
    RateLimitError,
    ModelNotAvailableError,
    GenerationError
)

async def robust_generation():
    factory = LLMProviderFactory.create_openai()
    
    try:
        response = await factory.generate("Hello world")
        return response.content
    except AuthenticationError:
        print("Check your API key")
    except RateLimitError:
        print("Rate limit exceeded, try again later")
    except ModelNotAvailableError:
        print("Model not available")
    except GenerationError as e:
        print(f"Generation failed: {e}")
```

## 🔧 Advanced Usage

### Custom Provider

```python
from llm_provider import BaseLLMProvider, ProviderConfig

class CustomProvider(BaseLLMProvider):
    async def initialize(self):
        # Initialize your custom provider
        pass
    
    async def generate(self, request):
        # Implement generation logic
        pass
    
    async def stream_generate(self, request):
        # Implement streaming logic
        pass
    
    def get_supported_models(self):
        return ["custom-model-1", "custom-model-2"]
    
    def validate_config(self):
        return True
    
    def get_provider_info(self):
        # Return provider information
        pass

# Register custom provider
factory = LLMProviderFactory()
factory.register_provider("custom", CustomProvider)
```

### Provider Information

```python
async def provider_info_example():
    factory = LLMProviderFactory()
    
    # Get all provider information
    all_providers = factory.get_provider_info()
    for info in all_providers:
        print(f"{info.display_name}: {info.supported_models}")
    
    # Get specific provider info
    openai_info = factory.get_provider_info("openai")
    print(f"OpenAI models: {openai_info.supported_models}")
```

## 📁 Project Structure

```
llm-provider-factory/
├── src/
│   └── llm_provider/
│       ├── __init__.py
│       ├── factory.py
│       ├── base_provider.py
│       ├── settings.py
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── openai_provider.py
│       │   ├── anthropic_provider.py
│       │   └── gemini_provider.py
│       └── utils/
│           ├── __init__.py
│           ├── config.py
│           ├── exceptions.py
│           └── logger.py
├── tests/
├── pyproject.toml
└── README.md
```

## 🧪 Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/llm_provider --cov-report=html

# Run specific test file
pytest tests/test_factory.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-provider`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Submit a pull request

### Adding a New Provider

1. Create a new provider class in `src/llm_provider/providers/`
2. Inherit from `BaseLLMProvider`
3. Implement all abstract methods
4. Add configuration class in `utils/config.py`
5. Register the provider in `factory.py`
6. Add tests in `tests/`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for their excellent API and documentation
- Anthropic for Claude's capabilities
- Google for Gemini's multimodal features
- The Python community for inspiration and tools

A unified, extensible interface for multiple Large Language Model providers. Built with clean architecture principles and SOLID design patterns.

## 🚀 Quick Start

```bash
pip install llm-provider
```

```python
from llm_provider import LLMProviderFactory, OpenAI

provider = LLMProviderFactory(OpenAI(api_key="your-key"))
response = provider.generate(prompt="Hello", history=[])
print(response.content)
```

## ✨ Features

- 🏭 **Factory Pattern**: Clean, consistent interface
- 🔌 **Extensible**: Easy to add new providers  
- 🛡️ **Type Safe**: Full typing support
- 🚀 **Production Ready**: Comprehensive error handling
- 📦 **Zero Dependencies**: Only requires `requests`

## 🔗 Links

- **PyPI**: https://pypi.org/project/llm-provider/
- **Test PyPI**: https://test.pypi.org/project/llm-provider/

## 📦 Supported Providers

- **OpenAI** (GPT-3.5, GPT-4)
- **Anthropic** (Claude models)
- **Google Gemini** (Gemini Pro, Flash)

## 📚 Documentation

See the package source code and examples in the repository.