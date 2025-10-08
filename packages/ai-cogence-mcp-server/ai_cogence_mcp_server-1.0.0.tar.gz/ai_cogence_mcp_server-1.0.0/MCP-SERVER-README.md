# MCP Server for AI Cogence Backend

## Overview

This MCP (Model Context Protocol) server exposes the AI Cogence backend's RAG capabilities, knowledge base, and chat functionality to AI assistants like Claude. It allows AI tools to directly query your knowledge base, perform semantic searches, and manage chat sessions.

## Features

### 🛠️ Tools Available

1. **`rag_query`** - Query the RAG system with natural language questions
   - Retrieves relevant documents from the knowledge base
   - Generates AI-powered answers using retrieved context
   - Maintains conversation continuity with session IDs

2. **`semantic_search`** - Perform vector similarity search
   - Find the most relevant text chunks based on embeddings
   - Configurable number of results (top_k)
   - Returns similarity scores

3. **`load_markdown_content`** - Index markdown files into the knowledge base
   - Loads content from the `/content` directory
   - Makes content searchable through RAG queries
   - Updates embeddings automatically

4. **`list_chat_sessions`** - View all chat sessions
   - Lists sessions with metadata
   - Shows creation and update timestamps
   - Configurable limit

5. **`get_session_messages`** - Retrieve conversation history
   - Get all messages from a specific session
   - Full conversation context
   - Chronological ordering

6. **`search_knowledge_base`** - Keyword-based search
   - Search by text content
   - Filter by source document
   - Metadata-aware queries

7. **`get_analytics`** - System usage statistics
   - Query counts and session metrics
   - Time-range filtering (today, week, month, all)
   - Performance insights

### 📚 Resources Available

1. **Content Resources** (`cogence://content/*`)
   - All markdown files from `/backend/content/`
   - Includes: home, about-us, services, etc.
   - Format: Markdown

2. **Knowledge Base** (`cogence://knowledge-base`)
   - Complete statistics about stored documents
   - Total chunks, sources, and sessions
   - Format: JSON

3. **Chat History** (`cogence://chat-history`)
   - Recent chat sessions (last 20)
   - Session IDs and timestamps
   - Format: JSON

## Installation

### 1. Install MCP Python SDK

```bash
cd /Users/infoobjects/Documents/Projects/ai-cogence-web/backend
source venv/bin/activate
pip install mcp
```

### 2. Verify Installation

```bash
python mcp_server.py --help
```

### 3. Configure Claude Desktop (Optional)

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ai-cogence-backend": {
      "command": "python",
      "args": [
        "/Users/infoobjects/Documents/Projects/ai-cogence-web/backend/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/infoobjects/Documents/Projects/ai-cogence-web/backend"
      }
    }
  }
}
```

## Usage

### Running the MCP Server

```bash
cd /Users/infoobjects/Documents/Projects/ai-cogence-web/backend
source venv/bin/activate
python mcp_server.py
```

The server runs on stdio and communicates via JSON-RPC 2.0.

### Example Tool Calls

#### 1. Query the RAG System

```json
{
  "tool": "rag_query",
  "arguments": {
    "question": "What services does AI Cogence offer?",
    "session_id": "optional-session-id"
  }
}
```

**Response:**
```json
{
  "answer": "AI Cogence offers RAG implementation, AI strategy consulting, fine-tuning services...",
  "sources": [
    {"content": "...", "metadata": {...}},
    {"content": "...", "metadata": {...}}
  ],
  "session_id": "...",
  "timestamp": "2025-10-08T10:30:00"
}
```

#### 2. Semantic Search

```json
{
  "tool": "semantic_search",
  "arguments": {
    "query": "machine learning consulting",
    "top_k": 5
  }
}
```

**Response:**
```json
{
  "query": "machine learning consulting",
  "results": [
    {
      "content": "Our AI strategy consulting helps businesses...",
      "metadata": {"source": "ai-strategy-consulting.md"},
      "similarity": 0.89
    },
    ...
  ],
  "count": 5
}
```

#### 3. Load Content

```json
{
  "tool": "load_markdown_content",
  "arguments": {
    "collection_name": "cogence_content"
  }
}
```

#### 4. Get Analytics

```json
{
  "tool": "get_analytics",
  "arguments": {
    "time_range": "week"
  }
}
```

**Response:**
```json
{
  "time_range": "week",
  "total_queries": 245,
  "unique_sessions": 87,
  "timestamp": "2025-10-08T10:30:00"
}
```

### Example Resource Access

#### Read Knowledge Base Stats

```
URI: cogence://knowledge-base
```

**Response:**
```json
{
  "total_chunks": 1234,
  "total_sources": 45,
  "total_sessions": 87,
  "timestamp": "2025-10-08T10:30:00"
}
```

#### Read Content File

```
URI: cogence://content/about-us.md
```

**Response:** (Full markdown content)

## Integration with Claude

Once configured, Claude can automatically:

1. **Answer questions about your business** using the RAG system
2. **Search your knowledge base** for specific information
3. **Access conversation history** for context
4. **View analytics** about system usage
5. **Read content files** directly

### Example Claude Interaction

**User:** "What do you know about AI Cogence's services?"

**Claude:** (Internally calls `rag_query` tool)
"AI Cogence offers several services including RAG implementation, AI strategy consulting, and fine-tuning services for enterprises..."

**User:** "Show me recent chat sessions"

**Claude:** (Internally calls `list_chat_sessions` tool)
"Here are the recent chat sessions: [lists sessions with timestamps]"

## Architecture

```
┌─────────────────────┐
│   AI Assistant      │
│   (Claude/etc)      │
└──────────┬──────────┘
           │ MCP Protocol
           │ (JSON-RPC)
┌──────────▼──────────┐
│   MCP Server        │
│   mcp_server.py     │
├─────────────────────┤
│ • Tools             │
│ • Resources         │
│ • Prompts           │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   Backend Services  │
├─────────────────────┤
│ • RAG Engine        │
│ • LangGraph         │
│ • PostgreSQL/pgvector│
│ • OpenAI Embeddings │
└─────────────────────┘
```

## Logging

The server logs to stdout with INFO level by default. Key events logged:

- Server startup/shutdown
- Tool invocations
- Database queries
- Errors and exceptions

View logs:
```bash
python mcp_server.py 2>&1 | tee mcp_server.log
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
brew services list | grep postgres

# Test database connection
psql -h localhost -p 5432 -U $(whoami) -d postgres
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install missing dependencies
pip install -r requirements.txt
pip install mcp
```

### Port Conflicts

The MCP server uses stdio, not network ports, so no port conflicts should occur.

## Security Considerations

1. **Database Access**: Server requires database credentials in `.env`
2. **API Keys**: OpenAI API keys must be configured
3. **Network**: stdio-based, no network exposure
4. **Authentication**: Inherits from backend authentication

## Development

### Adding New Tools

```python
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="my_new_tool",
            description="Description of what it does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    if name == "my_new_tool":
        return await handle_my_new_tool(arguments)
```

### Adding New Resources

```python
@mcp_server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        # ... existing resources ...
        Resource(
            uri="cogence://my-resource",
            name="My Resource",
            mimeType="application/json",
            description="Description of the resource"
        )
    ]
```

## Environment Variables

Required in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# OpenAI
OPENAI_API_KEY=sk-...

# Optional
LOG_LEVEL=INFO
```

## Performance

- **Latency**: ~100-500ms for RAG queries
- **Throughput**: Depends on PostgreSQL and OpenAI rate limits
- **Caching**: Embeddings are cached in database
- **Scaling**: Horizontal scaling via multiple server instances

## Support

For issues or questions:
1. Check logs: `python mcp_server.py 2>&1 | grep ERROR`
2. Review backend logs: `tail -f backend.log`
3. Test direct API: `curl http://localhost:5025/health`

## License

Same as parent project.

## Version History

- **v1.0.0** (2025-10-08): Initial release
  - 7 tools implemented
  - 3 resource types
  - Full RAG integration
  - PostgreSQL/pgvector support

