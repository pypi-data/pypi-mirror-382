# AI Cogence MCP Server

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.3.2-green.svg)](https://github.com/anthropics/mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Model Context Protocol (MCP) Server** for AI Cogence's RAG (Retrieval-Augmented Generation) backend. This server exposes powerful AI capabilities through the MCP protocol, allowing AI assistants like Claude to interact with your knowledge base, perform semantic search, manage chat sessions, and more.

## 🌟 Features

- **7 Powerful Tools** for AI interaction
- **3 Resource Types** for knowledge access
- **Async Operations** for high performance
- **PostgreSQL + pgvector** for semantic search
- **LangGraph Integration** for RAG workflows
- **OpenAI Embeddings** for vector similarity
- **Session Management** for conversation continuity
- **Analytics & Monitoring** built-in

## 📦 Installation

### Quick Install

```bash
pip install ai-cogence-mcp-server
```

### From Source

```bash
git clone https://github.com/ai-cogence/mcp-server.git
cd mcp-server
pip install -e .
```

### With Development Tools

```bash
pip install ai-cogence-mcp-server[dev]
```

## 🚀 Quick Start

### 1. Configure Environment

Create a `.env` file:

```bash
# Copy example configuration
cp .env.example .env

# Edit with your credentials
nano .env
```

Required variables:
```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database
OPENAI_API_KEY=sk-your-api-key
```

### 2. Run the Server

```bash
# Start MCP server
ai-cogence-mcp

# Or run directly
python -m mcp_server
```

The server runs on stdio and communicates via JSON-RPC 2.0.

### 3. Test the Server

```bash
# Run test suite
python test_mcp_server.py
```

## 🔧 Configuration

### Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "ai-cogence-backend": {
      "command": "ai-cogence-mcp",
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Custom Configuration

```python
from mcp_server import mcp_server

# Configure custom settings
mcp_server.config.update({
    "db_pool_size": 10,
    "log_level": "DEBUG"
})
```

## 🛠️ Available Tools

### 1. RAG Query
```json
{
  "tool": "rag_query",
  "arguments": {
    "question": "What services does AI Cogence offer?",
    "session_id": "optional-uuid"
  }
}
```

### 2. Semantic Search
```json
{
  "tool": "semantic_search",
  "arguments": {
    "query": "machine learning consulting",
    "top_k": 5
  }
}
```

### 3. List Chat Sessions
```json
{
  "tool": "list_chat_sessions",
  "arguments": {"limit": 20}
}
```

### 4. Get Session Messages
```json
{
  "tool": "get_session_messages",
  "arguments": {"session_id": "uuid"}
}
```

### 5. Search Knowledge Base
```json
{
  "tool": "search_knowledge_base",
  "arguments": {
    "query": "Sudhir Jangid",
    "source_filter": "about-us.md"
  }
}
```

### 6. Get Analytics
```json
{
  "tool": "get_analytics",
  "arguments": {"time_range": "week"}
}
```

### 7. Load Markdown Content
```json
{
  "tool": "load_markdown_content",
  "arguments": {"collection_name": "cogence_content"}
}
```

## 📚 Resources

- `cogence://content/*` - Markdown content files
- `cogence://knowledge-base` - Knowledge base statistics
- `cogence://chat-history` - Recent chat sessions

## 🏗️ Architecture

```
┌─────────────────────┐
│   AI Assistant      │
│   (Claude/etc)      │
└──────────┬──────────┘
           │ MCP Protocol
┌──────────▼──────────┐
│   MCP Server        │
│   (This Package)    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   Backend Services  │
│   • RAG/LangGraph   │
│   • PostgreSQL      │
│   • OpenAI          │
└─────────────────────┘
```

## 📖 Documentation

- [Full Documentation](./MCP-SERVER-README.md)
- [Setup Guide](./MCP-SETUP-COMPLETE.md)
- [API Reference](./docs/API.md)

## 🔒 Security

- Runs locally on your machine
- Uses stdio (no network exposure)
- Requires environment variables for credentials
- All data stays in your local database

## 🧪 Testing

```bash
# Run all tests
python test_mcp_server.py

# Run with pytest (if installed)
pytest tests/

# Run specific test
pytest tests/test_semantic_search.py
```

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/ai-cogence/mcp-server/issues)
- **Documentation**: [Full Docs](./MCP-SERVER-README.md)
- **Email**: contact@cogence.ai

## 🎯 Roadmap

- [ ] HTTP transport support
- [ ] WebSocket support
- [ ] Additional embedding providers
- [ ] Caching layer
- [ ] Prometheus metrics
- [ ] Docker image

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for the MCP protocol
- [LangChain](https://langchain.com) for the RAG framework
- [OpenAI](https://openai.com) for embeddings

---

Made with ❤️ by AI Cogence

