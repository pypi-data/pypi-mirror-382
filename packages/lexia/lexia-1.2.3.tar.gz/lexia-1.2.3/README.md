# Lexia Platform Integration Package

A clean, minimal Python package for seamless integration with the Lexia platform. This package provides essential components for AI agents to communicate with Lexia while maintaining platform-agnostic design.

## 🚀 Quick Start

### Install from PyPI (Recommended)
```bash
pip install lexia
```

### Install with web dependencies
```bash
pip install lexia[web]
```

### Install for development
```bash
pip install lexia[dev]
```

### Install from source
```bash
git clone https://github.com/Xalantico/lexia-pip.git
cd lexia-pip
pip install -e .
```

## 📦 Package Information

- **Package Name**: `lexia`
- **Version**: 1.1.0
- **Python**: >=3.8
- **License**: MIT
- **Dependencies**: requests, pydantic
- **Optional**: fastapi, uvicorn (web), pytest, black, flake8 (dev)

## 🎯 Purpose

This package provides a clean interface for AI agents to communicate with the Lexia platform. It handles all Lexia-specific communication while keeping your AI agent completely platform-agnostic.

## 🚀 Core Features

- **Real-time streaming** via Centrifugo
- **Backend communication** with Lexia API
- **Response formatting** for Lexia compatibility
- **Data validation** with Pydantic models
- **Error handling** and logging
- **FastAPI integration** with standard endpoints (optional)
- **Dynamic configuration** from request data
- **Header forwarding** (x-tenant, etc.) to Lexia API
- **Easy variable access** with Variables helper class
- **User memory handling** with MemoryHelper for personalized responses
- **Graceful fallback** when web dependencies aren't available

## 📁 Package Structure

```
lexia/
├── __init__.py             # Package exports with optional web imports
├── models.py               # Lexia data models (ChatMessage, ChatResponse, Variable)
├── response_handler.py     # Response creation utilities
├── unified_handler.py      # Main communication interface
├── api_client.py           # HTTP communication with Lexia backend
├── centrifugo_client.py    # Real-time updates via Centrifugo
├── utils.py                # Platform utilities
├── web/                    # FastAPI web framework utilities (optional)
│   ├── __init__.py
│   ├── app_factory.py
│   └── endpoints.py
└── requirements.txt        # Package dependencies
```

**Note**: The `web/` module is optional and will gracefully fall back if FastAPI dependencies aren't available.

## 🚀 Usage Examples

### Basic Usage
```python
from lexia import LexiaHandler, ChatMessage

# Initialize the handler
lexia = LexiaHandler()

# Use in your AI agent
async def process_message(data: ChatMessage):
    # Your AI logic here...
    response = "Hello from your AI agent!"
    lexia.complete_response(data, response)
```

### FastAPI Integration
```python
from fastapi import FastAPI
from lexia import create_lexia_app, add_standard_endpoints, LexiaHandler

# Create FastAPI app
app = create_lexia_app(title="My AI Agent")

# Initialize Lexia handler
lexia = LexiaHandler()

# Add standard endpoints
add_standard_endpoints(
    app, 
    lexia_handler=lexia,
    process_message_func=your_ai_function
)
```

## 🔧 Core Components

### LexiaHandler (Main Interface)
Single, clean interface for all Lexia communication:

```python
from lexia import LexiaHandler

lexia = LexiaHandler()

# Stream AI response chunks
lexia.stream_chunk(data, content)

# Complete AI response (handles all Lexia communication)
lexia.complete_response(data, full_response)

# Send error messages
lexia.send_error(data, error_message)

# Update Centrifugo configuration dynamically
lexia.update_centrifugo_config(stream_url, stream_token)

# Headers (like x-tenant) are automatically forwarded to Lexia API
# No additional configuration needed - just include headers in your request
```

### Data Models
Lexia's expected data formats:

```python
from lexia import ChatMessage, ChatResponse, Variable

# ChatMessage - Lexia's request format with all required fields
# ChatResponse - Lexia's expected response format  
# Variable - Environment variables from Lexia request
```

### Variables Helper
Easy access to environment variables from Lexia requests:

```python
from lexia import Variables

# Create variables helper from request data
vars = Variables(data.variables)

# Get any variable by name
openai_key = vars.get("OPENAI_API_KEY")
anthropic_key = vars.get("ANTHROPIC_API_KEY")
custom_var = vars.get("CUSTOM_VAR")

# Convenience methods for common API keys
openai_key = vars.get_openai_key()
anthropic_key = vars.get_anthropic_key()
groq_key = vars.get_groq_key()
database_url = vars.get_database_url()

# Check if variable exists
if vars.has("OPENAI_API_KEY"):
    key = vars.get("OPENAI_API_KEY")

# Get all variable names
all_names = vars.list_names()  # ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", ...]

# Convert to dictionary
vars_dict = vars.to_dict()  # {"OPENAI_API_KEY": "sk-...", ...}
```

### Memory Helper
Easy access to user memory data from Lexia requests:

```python
from lexia import MemoryHelper

# Create memory helper from request data
memory = MemoryHelper(data.memory)

# Get user information
user_name = memory.get_name()
user_goals = memory.get_goals()
user_location = memory.get_location()
user_interests = memory.get_interests()
user_preferences = memory.get_preferences()
user_experiences = memory.get_past_experiences()

# Check if memory data exists
if memory.has_name():
    print(f"User: {memory.get_name()}")
if memory.has_goals():
    print(f"Goals: {memory.get_goals()}")
if memory.has_location():
    print(f"Location: {memory.get_location()}")

# Convert to dictionary
memory_dict = memory.to_dict()

# Check if memory is empty
if not memory.is_empty():
    # Process user memory data
    pass
```

**Supported Memory Formats:**
- `"memory": []` - Empty array (treated as empty memory)
- `"memory": {}` - Empty object (treated as empty memory)  
- `"memory": {"name": "John", "goals": [...]}` - Structured memory
- `"memory": null` - Null value (treated as empty memory)

### Response Handler
Create Lexia-compatible responses:

```python
from lexia import create_success_response
from lexia.response_handler import create_complete_response

# Create immediate success response
response = create_success_response(
    response_uuid="uuid123",
    thread_id="thread456"
)

# Create complete response with usage info (used internally by LexiaHandler)
complete_response = create_complete_response(
    response_uuid="uuid123",
    thread_id="thread456",
    content="Full AI response",
    usage_info={"prompt_tokens": 10, "completion_tokens": 50}
)
```

## 💡 Complete Example: AI Agent with FastAPI

```python
import asyncio
from fastapi import FastAPI
from lexia import (
    LexiaHandler, 
    ChatMessage, 
    Variables,
    MemoryHelper,
    create_lexia_app,
    add_standard_endpoints
)

# Initialize services
lexia = LexiaHandler()

# Create FastAPI app
app = create_lexia_app(
    title="My AI Agent",
    version="1.1.0",
    description="Custom AI agent with Lexia integration"
)

# Define your AI logic
async def process_message(data: ChatMessage):
    """Your custom AI processing logic goes here."""
    try:
        # Easy access to environment variables
        vars = Variables(data.variables)
        
        # Easy access to user memory
        memory = MemoryHelper(data.memory)
        
        # Get API keys for different AI providers
        openai_key = vars.get_openai_key()
        anthropic_key = vars.get_anthropic_key()
        
        # Get custom variables
        custom_config = vars.get("CUSTOM_CONFIG")
        database_url = vars.get("DATABASE_URL")
        
        # Get user information for personalized responses
        user_name = memory.get_name()
        user_goals = memory.get_goals()
        user_location = memory.get_location()
        user_interests = memory.get_interests()
        
        # Check if required variables exist
        if not openai_key and not anthropic_key:
            lexia.send_error(data, "No AI API key provided")
            return
        
        # Create personalized response based on user memory
        if memory.has_name():
            response = f"Hello {user_name}! AI Agent processed: {data.message}"
        else:
            response = f"AI Agent processed: {data.message}"
        
        # Add user-specific context if available
        if memory.has_goals():
            response += f"\n\nI see your goals include: {', '.join(user_goals)}"
        
        # Stream response chunks (optional)
        for word in response.split():
            lexia.stream_chunk(data, word + " ")
            await asyncio.sleep(0.1)
        
        # Complete the response
        lexia.complete_response(data, response)
        
    except Exception as e:
        # Handle errors appropriately
        lexia.send_error(data, f"Error processing message: {e}")

# Add all standard Lexia endpoints
add_standard_endpoints(
    app, 
    conversation_manager=None,
    lexia_handler=lexia,
    process_message_func=process_message
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🔄 Integration Flow

```
Your AI Agent → LexiaHandler → Lexia Platform
     ↓              ↓              ↓
  AI/LLM Logic   Communication   Real-time + Backend
```

Your AI agent focuses on AI logic, this package handles all Lexia communication complexity behind a clean interface.

## 📋 Development Setup

### Using Make (Recommended)
```bash
# Show available commands
make help

# Setup development environment
make dev
source lexia_env/bin/activate
make deps

# Build and test
make build
make test
make install
```

### Manual Setup
```bash
# Create virtual environment
python3 -m venv lexia_env
source lexia_env/bin/activate

# Install dependencies
pip install -r lexia/requirements.txt
pip install build twine

# Build package
python -m build

# Install locally
pip install -e .
```

## 🧪 Testing

```python
import pytest
from lexia import LexiaHandler, ChatMessage

def test_lexia_handler():
    """Test basic LexiaHandler functionality."""
    handler = LexiaHandler()
    
    # Create test data
    test_data = ChatMessage(
        thread_id="test123",
        model="gpt-4",
        message="Hello",
        conversation_id=1,
        response_uuid="uuid123",
        message_uuid="msg123",
        channel="test",
        file_type="",
        file_url="",
        variables=[],
        url="http://test.com",
        url_update="",
        url_upload="",
        force_search=False,
        system_message=None,
        memory=[],
        project_system_message=None,
        first_message=False,
        project_id="",
        project_files=None
    )
    
    # Test that handler can be created
    assert handler is not None
    assert hasattr(handler, 'stream_chunk')
    assert hasattr(handler, 'complete_response')
    assert hasattr(handler, 'send_error')
    assert hasattr(handler, 'update_centrifugo_config')

if __name__ == "__main__":
    pytest.main([__file__])
```

## 🚨 Common Issues and Solutions

### Import Error
```bash
ModuleNotFoundError: No module named 'lexia'
```
**Solution**: Ensure you're in the correct directory or add the lexia folder to your Python path.

### Missing Dependencies
```bash
ImportError: No module named 'fastapi'
```
**Solution**: Install requirements: `pip install -r lexia/requirements.txt` or use `pip install lexia[web]`

### Lexia Communication Fails
**Solution**: Verify that your environment variables and API keys are properly configured in the Lexia request variables.

## 📦 Publishing

### Test PyPI
```bash
make build
make publish-test
```

### Production PyPI
```bash
make build
make publish
```

## 🎯 Design Principles

1. **Single Responsibility**: Each component has one clear purpose
2. **Clean Interface**: Simple, intuitive methods
3. **Platform Agnostic**: Your AI agent doesn't know about Lexia internals
4. **Minimal Dependencies**: Only what's absolutely necessary
5. **Easy Testing**: Simple, focused components
6. **Dynamic Configuration**: Adapts to request-specific settings

## 🚀 Benefits

- **Clean separation** between your AI agent and Lexia
- **Easy to maintain** - all Lexia logic in one place
- **Easy to replace** - switch platforms by replacing this package
- **Professional structure** - clean, organized code
- **Fast development** - no complex integrations to manage
- **Drop-in replacement** - copy folder and start using immediately
- **Dynamic configuration** - adapts to different Lexia environments

## 📞 Support

This package is designed to be a drop-in solution - just `pip install lexia` and start building your AI agent! All Lexia communication is handled automatically, standard endpoints are provided out-of-the-box, and your AI agent remains completely platform-agnostic.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📚 Documentation

For more detailed documentation, please refer to the inline code comments and examples provided in this README.