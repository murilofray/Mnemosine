# Mnemosine Backend

## 🚀 Features

- **FastAPI** - High-performance async API framework
- **LangGraph** - AI agent workflow orchestration
- **Pydantic AI** - Modern LLM integration
- **JWT Authentication** - Secure token-based authentication
- **Rate Limiting** - Built-in API protection
- **Input Sanitization** - Prompt injection prevention
- **Comprehensive Logging** - Pydantic LogFire integration
- **Type Safety** - Full Pydantic and Python typing support

## 🏗️ Architecture

```
mnemosine-backend/
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── cli.py                   # CLI tools with Typer
│   │
│   ├── config/
│   │   └── settings.py          # Pydantic BaseSettings configuration
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── api.py           # Main API router
│   │       ├── auth.py          # Authentication endpoints
│   │       └── agent.py         # AI agent endpoints
│   │
│   ├── core/
│   │   ├── langgraph/
│   │   │   ├── graph.py         # LangGraph workflows
│   │   │   └── tools.py         # Agent tools
│   │   ├── prompts/
│   │   │   ├── __init__.py      # Prompt management
│   │   │   └── system.md        # System prompt template
│   │   └── security/
│   │       ├── auth.py          # JWT utilities
│   │       └── limiter.py       # Rate limiting
│   │
│   ├── middleware/
│   │   └── errors.py            # Error handling
│   │
│   ├── models/
│   │   └── user.py              # User models
│   │
│   ├── schemas/
│   │   ├── auth.py              # Authentication schemas
│   │   └── agent.py             # Agent request/response schemas
│   │
│   ├── services/
│   │   ├── agent.py             # AI agent service
│   │   └── user.py              # User service
│   │
│   └── utils/
│       └── sanitize.py          # Input sanitization utilities
│
├── metrics/                     # LLM evaluation tools
├── tests/                       # Test suite
└── pyproject.toml              # Project configuration
```

## 🛠️ Quick Start

### Prerequisites

- Python 3.12+
- UV package manager

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd mnemosine-backend
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment:**
   ```bash
   # Generate a secret key
   uv run python -m app.cli generate-secret-key
   
   # Create .env file (copy from .env.example)
   echo 'SECRET_KEY="your-generated-secret-key"' > .env
   echo 'ADMIN_USERNAME="admin"' >> .env
   echo 'ADMIN_PASSWORD="your-secure-password"' >> .env
   echo 'GEMINI_API_KEY="your-gemini-key"' >> .env
   echo 'DEFAULT_PROVIDER="gemini"' >> .env
   ```

4. **Validate configuration:**
   ```bash
   uv run python -m app.cli validate-config
   ```

5. **Run the server:**
   ```bash
   uv run python -m app.cli run-server --reload
   ```

   Or directly:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

```bash
# Application
SECRET_KEY="your-secret-key-here"
DEBUG=false
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="your-secure-password"

# Database (if using PostgreSQL)
DATABASE_URL="postgresql://user:password@localhost:5432/mnemosine_db"

# LLM APIs
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"
GEMINI_API_KEY="your-gemini-key"
DEFAULT_MODEL="gemini-1.5-flash"
DEFAULT_PROVIDER="gemini"

# Security
RATE_LIMIT_PER_MINUTE=60
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Observability
LOGFIRE_TOKEN="your-logfire-token"
LOGFIRE_ENABLED=true
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_auth.py -v
```

## 🛡️ Security Features

- **JWT Authentication** - Secure token-based auth
- **Rate Limiting** - Configurable per-endpoint limits
- **Input Sanitization** - Prevents prompt injection attacks
- **CORS Protection** - Configurable origins
- **Error Handling** - Unified error responses without info leakage

## 📊 Monitoring & Observability

- **Pydantic LogFire** - Comprehensive logging and monitoring
- **Health Checks** - Built-in health endpoints
- **Metrics Collection** - Request/response metrics
- **Error Tracking** - Detailed error logging

## 🔧 CLI Tools

The project includes useful CLI commands:

```bash
# Generate secret key
uv run python -m app.cli generate-secret-key

# Validate configuration
uv run python -m app.cli validate-config

# Run server with custom settings
uv run python -m app.cli run-server --host 0.0.0.0 --port 8000 --reload

# Test authentication
uv run python -m app.cli test-auth admin your-password

# Hash a password
uv run python -m app.cli hash-password your-password
```

## 🏗️ Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
uv run black .

# Sort imports
uv run isort .

# Type checking
uv run mypy app/
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
uv run pre-commit install
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the documentation
2. Run `uv run python -m app.cli validate-config`
3. Check the logs
4. Open an issue on GitHub

---

**Built with ❤️ using FastAPI, LangGraph, and modern Python tooling.**
