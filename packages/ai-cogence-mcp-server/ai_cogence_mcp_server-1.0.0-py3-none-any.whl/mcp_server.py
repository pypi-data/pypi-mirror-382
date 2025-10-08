"""
MCP (Model Context Protocol) Server for AI Cogence Backend

This server exposes the RAG capabilities, chat functionality, and knowledge base
through the Model Context Protocol, allowing AI assistants to interact with
the backend services.
"""

import asyncio
import json
import logging
from typing import Any, Sequence
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Import backend components
from connectors.db import init_db_pool, cleanup, db_pool, embeddings
from controllers.chat_controller import init_langgraph
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp_server = Server("ai-cogence-backend")

# Global state
graph = None
retriever = None


@mcp_server.list_resources()
async def list_resources() -> list[Resource]:
    """
    List all available resources from the knowledge base.
    Resources include markdown content, documents, and stored data.
    """
    resources = []
    
    # Add markdown content resources
    content_dir = os.path.join(os.path.dirname(__file__), "content")
    if os.path.exists(content_dir):
        for filename in os.listdir(content_dir):
            if filename.endswith('.md'):
                uri = f"cogence://content/{filename}"
                name = filename.replace('-', ' ').replace('.md', '').title()
                resources.append(
                    Resource(
                        uri=uri,
                        name=f"Content: {name}",
                        mimeType="text/markdown",
                        description=f"Cogence website content about {name}"
                    )
                )
    
    # Add knowledge base resource
    resources.append(
        Resource(
            uri="cogence://knowledge-base",
            name="Knowledge Base",
            mimeType="application/json",
            description="Complete knowledge base with all stored documents and embeddings"
        )
    )
    
    # Add chat history resource
    resources.append(
        Resource(
            uri="cogence://chat-history",
            name="Recent Chat History",
            mimeType="application/json",
            description="Recent chat conversations and their context"
        )
    )
    
    return resources


@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """
    Read a specific resource by URI.
    """
    logger.info(f"Reading resource: {uri}")
    
    if uri.startswith("cogence://content/"):
        # Extract filename and read markdown content
        filename = uri.replace("cogence://content/", "")
        content_path = os.path.join(os.path.dirname(__file__), "content", filename)
        
        if os.path.exists(content_path):
            with open(content_path, 'r') as f:
                content = f.read()
            return content
        else:
            return f"Content file not found: {filename}"
    
    elif uri == "cogence://knowledge-base":
        # Return knowledge base statistics
        if db_pool:
            async with db_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        SELECT 
                            COUNT(*) as total_chunks,
                            COUNT(DISTINCT metadata->>'source') as total_sources,
                            COUNT(DISTINCT session_id) as total_sessions
                        FROM langchain_pg_embedding
                    """)
                    stats = await cur.fetchone()
                    
                    return json.dumps({
                        "total_chunks": stats[0] if stats else 0,
                        "total_sources": stats[1] if stats else 0,
                        "total_sessions": stats[2] if stats else 0,
                        "timestamp": datetime.now().isoformat()
                    }, indent=2)
        return json.dumps({"error": "Database not connected"})
    
    elif uri == "cogence://chat-history":
        # Return recent chat history
        if db_pool:
            async with db_pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        SELECT session_id, created_at
                        FROM chat_sessions
                        ORDER BY created_at DESC
                        LIMIT 20
                    """)
                    sessions = await cur.fetchall()
                    
                    history = []
                    for session in sessions:
                        history.append({
                            "session_id": str(session[0]),
                            "created_at": session[1].isoformat() if session[1] else None
                        })
                    
                    return json.dumps({
                        "recent_sessions": history,
                        "count": len(history)
                    }, indent=2)
        return json.dumps({"error": "Database not connected"})
    
    return f"Unknown resource URI: {uri}"


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools that can be called through MCP.
    """
    return [
        Tool(
            name="rag_query",
            description="Query the RAG (Retrieval-Augmented Generation) system with a question. "
                       "This searches the knowledge base and generates an AI-powered answer based on retrieved documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the RAG system"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional session ID for conversation continuity"
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="semantic_search",
            description="Perform semantic search on the knowledge base to find relevant documents and chunks. "
                       "Returns the most relevant text chunks based on embedding similarity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="load_markdown_content",
            description="Load and index markdown content from the content directory into the knowledge base. "
                       "This makes the content searchable through RAG queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Name for the collection (default: cogence_content)",
                        "default": "cogence_content"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="list_chat_sessions",
            description="List all chat sessions with their metadata. "
                       "Useful for understanding conversation history and context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of sessions to return (default: 20)",
                        "default": 20
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_session_messages",
            description="Get all messages from a specific chat session. "
                       "Returns the full conversation history for the given session.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID to retrieve messages from"
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="search_knowledge_base",
            description="Search the knowledge base for specific content by keyword or metadata. "
                       "Supports filtering by source, date, or other metadata fields.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query or keyword"
                    },
                    "source_filter": {
                        "type": "string",
                        "description": "Optional filter by source document"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_analytics",
            description="Get analytics and usage statistics for the system. "
                       "Returns metrics about queries, sessions, and knowledge base usage.",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "description": "Time range for analytics (today, week, month, all)",
                        "default": "today"
                    }
                },
                "required": []
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """
    Execute a tool call and return results.
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        if name == "rag_query":
            return await handle_rag_query(arguments)
        
        elif name == "semantic_search":
            return await handle_semantic_search(arguments)
        
        elif name == "load_markdown_content":
            return await handle_load_markdown(arguments)
        
        elif name == "list_chat_sessions":
            return await handle_list_sessions(arguments)
        
        elif name == "get_session_messages":
            return await handle_get_messages(arguments)
        
        elif name == "search_knowledge_base":
            return await handle_search_kb(arguments)
        
        elif name == "get_analytics":
            return await handle_get_analytics(arguments)
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error executing tool: {str(e)}"
        )]


async def handle_rag_query(arguments: dict) -> Sequence[TextContent]:
    """Handle RAG query tool call."""
    question = arguments.get("question")
    session_id = arguments.get("session_id")
    
    if not question:
        return [TextContent(type="text", text="Error: question is required")]
    
    global graph
    if not graph:
        return [TextContent(type="text", text="Error: RAG system not initialized")]
    
    # Execute RAG query through the graph
    try:
        from graph.main import execute_graph_stream
        
        result = {"messages": []}
        async for chunk in execute_graph_stream(question, session_id):
            if isinstance(chunk, dict) and "answer" in chunk:
                result = chunk
                break
        
        answer = result.get("answer", "No answer generated")
        sources = result.get("sources", [])
        
        response = {
            "answer": answer,
            "sources": sources,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing RAG query: {str(e)}"
        )]


async def handle_semantic_search(arguments: dict) -> Sequence[TextContent]:
    """Handle semantic search tool call."""
    query = arguments.get("query")
    top_k = arguments.get("top_k", 5)
    
    if not query:
        return [TextContent(type="text", text="Error: query is required")]
    
    if not db_pool:
        return [TextContent(type="text", text="Error: Database not connected")]
    
    try:
        # Get embedding for query
        query_embedding = embeddings.embed_query(query)
        
        # Search using pgvector
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT 
                        document,
                        metadata,
                        1 - (embedding <=> %s::vector) as similarity
                    FROM langchain_pg_embedding
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, top_k))
                
                results = await cur.fetchall()
                
                search_results = []
                for row in results:
                    search_results.append({
                        "content": row[0],
                        "metadata": row[1],
                        "similarity": float(row[2])
                    })
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "query": query,
                        "results": search_results,
                        "count": len(search_results)
                    }, indent=2)
                )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error performing semantic search: {str(e)}"
        )]


async def handle_load_markdown(arguments: dict) -> Sequence[TextContent]:
    """Handle markdown content loading."""
    collection_name = arguments.get("collection_name", "cogence_content")
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": False,
            "message": "Markdown loading functionality is available via website_loader_route API",
            "collection": collection_name,
            "timestamp": datetime.now().isoformat()
        }, indent=2)
    )]


async def handle_list_sessions(arguments: dict) -> Sequence[TextContent]:
    """Handle list chat sessions tool call."""
    limit = arguments.get("limit", 20)
    
    if not db_pool:
        return [TextContent(type="text", text="Error: Database not connected")]
    
    try:
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT 
                        session_id,
                        created_at,
                        updated_at,
                        metadata
                    FROM chat_sessions
                    ORDER BY updated_at DESC
                    LIMIT %s
                """, (limit,))
                
                sessions = await cur.fetchall()
                
                session_list = []
                for session in sessions:
                    session_list.append({
                        "session_id": str(session[0]),
                        "created_at": session[1].isoformat() if session[1] else None,
                        "updated_at": session[2].isoformat() if session[2] else None,
                        "metadata": session[3]
                    })
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "sessions": session_list,
                        "count": len(session_list)
                    }, indent=2)
                )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error listing sessions: {str(e)}"
        )]


async def handle_get_messages(arguments: dict) -> Sequence[TextContent]:
    """Handle get session messages tool call."""
    session_id = arguments.get("session_id")
    
    if not session_id:
        return [TextContent(type="text", text="Error: session_id is required")]
    
    if not db_pool:
        return [TextContent(type="text", text="Error: Database not connected")]
    
    try:
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT 
                        message,
                        response,
                        created_at,
                        metadata
                    FROM chat_messages
                    WHERE session_id = %s
                    ORDER BY created_at ASC
                """, (session_id,))
                
                messages = await cur.fetchall()
                
                message_list = []
                for msg in messages:
                    message_list.append({
                        "message": msg[0],
                        "response": msg[1],
                        "created_at": msg[2].isoformat() if msg[2] else None,
                        "metadata": msg[3]
                    })
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "session_id": session_id,
                        "messages": message_list,
                        "count": len(message_list)
                    }, indent=2)
                )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting messages: {str(e)}"
        )]


async def handle_search_kb(arguments: dict) -> Sequence[TextContent]:
    """Handle knowledge base search."""
    query = arguments.get("query")
    source_filter = arguments.get("source_filter")
    
    if not query:
        return [TextContent(type="text", text="Error: query is required")]
    
    if not db_pool:
        return [TextContent(type="text", text="Error: Database not connected")]
    
    try:
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                if source_filter:
                    await cur.execute("""
                        SELECT document, metadata
                        FROM langchain_pg_embedding
                        WHERE document ILIKE %s
                        AND metadata->>'source' ILIKE %s
                        LIMIT 20
                    """, (f"%{query}%", f"%{source_filter}%"))
                else:
                    await cur.execute("""
                        SELECT document, metadata
                        FROM langchain_pg_embedding
                        WHERE document ILIKE %s
                        LIMIT 20
                    """, (f"%{query}%",))
                
                results = await cur.fetchall()
                
                search_results = []
                for row in results:
                    search_results.append({
                        "content": row[0],
                        "metadata": row[1]
                    })
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "query": query,
                        "results": search_results,
                        "count": len(search_results)
                    }, indent=2)
                )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error searching knowledge base: {str(e)}"
        )]


async def handle_get_analytics(arguments: dict) -> Sequence[TextContent]:
    """Handle analytics retrieval."""
    time_range = arguments.get("time_range", "today")
    
    if not db_pool:
        return [TextContent(type="text", text="Error: Database not connected")]
    
    try:
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Get query statistics
                if time_range == "today":
                    time_filter = "created_at >= CURRENT_DATE"
                elif time_range == "week":
                    time_filter = "created_at >= CURRENT_DATE - INTERVAL '7 days'"
                elif time_range == "month":
                    time_filter = "created_at >= CURRENT_DATE - INTERVAL '30 days'"
                else:
                    time_filter = "TRUE"
                
                await cur.execute(f"""
                    SELECT 
                        COUNT(*) as total_queries,
                        COUNT(DISTINCT session_id) as unique_sessions
                    FROM chat_messages
                    WHERE {time_filter}
                """)
                
                stats = await cur.fetchone()
                
                analytics = {
                    "time_range": time_range,
                    "total_queries": stats[0] if stats else 0,
                    "unique_sessions": stats[1] if stats else 0,
                    "timestamp": datetime.now().isoformat()
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(analytics, indent=2)
                )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting analytics: {str(e)}"
        )]


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting AI Cogence MCP Server...")
    
    # Initialize database and services
    try:
        await init_db_pool()
        logger.info("Database initialized")
        
        global graph
        graph = await init_langgraph()
        logger.info("LangGraph initialized")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}", exc_info=True)
        raise
    
    # Run the MCP server
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP Server running on stdio")
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options()
            )
    finally:
        await cleanup()
        logger.info("MCP Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())

