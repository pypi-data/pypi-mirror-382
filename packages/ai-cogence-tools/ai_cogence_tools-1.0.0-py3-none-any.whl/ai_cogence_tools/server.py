#!/usr/bin/env python3
"""
AI Cogence MCP Tools Server

This is a proper MCP server that exposes AI Cogence tools via the Model Context Protocol.
Users install this package and connect to it via MCP clients (like Claude Desktop).

NOT an HTTP API - this is the MCP protocol for tool-based interaction.
"""

import asyncio
import sys
import os
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, ResourceTemplate
from dotenv import load_dotenv
import logging

# Add backend to path to import existing services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.db import init_db_pool, cleanup, db_pool, embeddings
from controllers.chat_controller import response_generation, init_langgraph
from controllers.s3_controller import fetch_and_chunk_s3_docs
from models.chat_model import ChatRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-cogence-tools")

# Load environment
load_dotenv()

# Create MCP server
server = Server("ai-cogence-tools")

# ============================================================================
# Tool Definitions
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available AI Cogence tools"""
    return [
        Tool(
            name="rag_query",
            description="Execute a RAG query to get AI-powered answers with sources from the knowledge base. Use this when you need to answer questions using AI Cogence's knowledge.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional session ID for conversation context"
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="semantic_search",
            description="Perform semantic search using vector embeddings to find similar content. Use this for finding related documents or content discovery.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_chat_sessions",
            description="List all chat sessions with metadata. Use this to see conversation history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of sessions to return",
                        "default": 20
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_session_messages",
            description="Get all messages for a specific chat session. Use this to retrieve conversation history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to retrieve messages for"
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="get_analytics",
            description="Get usage analytics and metrics. Use this for monitoring and insights.",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "description": "Time range: today, week, month, all",
                        "default": "today"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="search_knowledge_base",
            description="Search the knowledge base using keyword matching. Use this for finding specific content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="ingest_documents",
            description="Ingest documents from S3 bucket into the vector database. Loads documents, chunks them, creates embeddings, and stores them for RAG queries. Use this to update the knowledge base with new content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Force refresh even if documents are already ingested",
                        "default": False
                    }
                },
                "required": []
            }
        )
    ]

# ============================================================================
# Tool Implementations (using existing backend services)
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Execute a tool - routes to appropriate handler"""
    
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        if name == "rag_query":
            return await handle_rag_query(arguments)
        elif name == "semantic_search":
            return await handle_semantic_search(arguments)
        elif name == "list_chat_sessions":
            return await handle_list_sessions(arguments)
        elif name == "get_session_messages":
            return await handle_get_messages(arguments)
        elif name == "get_analytics":
            return await handle_get_analytics(arguments)
        elif name == "search_knowledge_base":
            return await handle_search_kb(arguments)
        elif name == "ingest_documents":
            return await handle_ingest_documents(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_rag_query(arguments: dict) -> Sequence[TextContent]:
    """RAG query tool - uses existing response_generation service"""
    question = arguments.get("question")
    session_id = arguments.get("session_id", "mcp-session")
    
    if not question:
        return [TextContent(type="text", text="Error: question is required")]
    
    # Create ChatRequest using existing model
    chat_request = ChatRequest(
        user_query=question,
        domain=None,
        content_type="mcp"
    )
    
    full_response = ""
    sources = []
    demo = None
    
    # Use existing response_generation service (same as chat_route.py and voice_route.py)
    async for event in response_generation(session_id, chat_request):
        if isinstance(event, dict):
            if event.get("type") == "final":
                full_response = event.get("response", "")
                sources = event.get("sources", [])
                demo = event.get("demo")
    
    result = {
        "answer": full_response,
        "sources": [{"content": s.get("content", ""), "metadata": s.get("metadata", {})} for s in sources],
        "session_id": session_id
    }
    
    # Include demo if present
    if demo:
        result["demo"] = demo
    
    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_semantic_search(arguments: dict) -> Sequence[TextContent]:
    """Semantic search tool - uses existing embeddings and pgvector"""
    query = arguments.get("query")
    top_k = arguments.get("top_k", 5)
    
    if not query:
        return [TextContent(type="text", text="Error: query is required")]
    
    # Use existing embedding service
    query_embedding = embeddings.embed_query(query)
    
    # Query existing vector database
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT content, metadata, 
                       1 - (embedding <=> %s::vector) as similarity
                FROM embeddings
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, top_k))
            
            results = []
            async for row in cur:
                results.append({
                    "content": row[0],
                    "metadata": row[1],
                    "similarity": float(row[2])
                })
    
    import json
    return [TextContent(type="text", text=json.dumps({"results": results, "count": len(results)}, indent=2))]


async def handle_list_sessions(arguments: dict) -> Sequence[TextContent]:
    """List sessions tool - uses existing database"""
    limit = arguments.get("limit", 20)
    
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT session_id, created_at, updated_at
                FROM sessions
                ORDER BY updated_at DESC
                LIMIT %s
            """, (limit,))
            
            sessions = []
            async for row in cur:
                sessions.append({
                    "session_id": row[0],
                    "created_at": row[1].isoformat() if row[1] else None,
                    "updated_at": row[2].isoformat() if row[2] else None
                })
    
    import json
    return [TextContent(type="text", text=json.dumps({"sessions": sessions, "count": len(sessions)}, indent=2))]


async def handle_get_messages(arguments: dict) -> Sequence[TextContent]:
    """Get messages tool - uses existing database"""
    session_id = arguments.get("session_id")
    
    if not session_id:
        return [TextContent(type="text", text="Error: session_id is required")]
    
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT role, content, created_at
                FROM messages
                WHERE session_id = %s
                ORDER BY created_at ASC
            """, (session_id,))
            
            messages = []
            async for row in cur:
                messages.append({
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2].isoformat() if row[2] else None
                })
    
    import json
    return [TextContent(type="text", text=json.dumps({"session_id": session_id, "messages": messages}, indent=2))]


async def handle_get_analytics(arguments: dict) -> Sequence[TextContent]:
    """Get analytics tool - uses existing analytics infrastructure"""
    time_range = arguments.get("time_range", "today")
    
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            # Get total queries
            await cur.execute("SELECT COUNT(*) FROM chat_messages")
            row = await cur.fetchone()
            total_queries = row[0] if row else 0
            
            # Get unique sessions
            await cur.execute("SELECT COUNT(DISTINCT session_id) FROM sessions")
            row = await cur.fetchone()
            unique_sessions = row[0] if row else 0
    
    import json
    result = {
        "time_range": time_range,
        "total_queries": total_queries,
        "unique_sessions": unique_sessions
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_search_kb(arguments: dict) -> Sequence[TextContent]:
    """Search knowledge base tool - uses existing database"""
    query = arguments.get("query")
    limit = arguments.get("limit", 10)
    
    if not query:
        return [TextContent(type="text", text="Error: query is required")]
    
    async with db_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT content, metadata
                FROM embeddings
                WHERE content ILIKE %s
                LIMIT %s
            """, (f"%{query}%", limit))
            
            results = []
            async for row in cur:
                results.append({
                    "content": row[0],
                    "metadata": row[1]
                })
    
    import json
    return [TextContent(type="text", text=json.dumps({"results": results, "count": len(results)}, indent=2))]


async def handle_ingest_documents(arguments: dict) -> Sequence[TextContent]:
    """Ingest documents tool - uses existing S3 controller"""
    force_refresh = arguments.get("force_refresh", False)
    
    try:
        logger.info("Starting document ingestion from S3...")
        
        # Use existing S3 controller function
        result = await fetch_and_chunk_s3_docs()
        
        response = {
            "status": "success",
            "message": result.get("message", "Documents ingested successfully"),
            "chunks_created": len(result.get("chunks", [])),
            "details": "Documents loaded from S3, chunked, embedded, and stored in vector database"
        }
        
        import json
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
    
    except Exception as e:
        logger.error(f"Error in ingest_documents: {e}", exc_info=True)
        import json
        return [TextContent(type="text", text=json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2))]


# ============================================================================
# Resources (optional - expose knowledge base content)
# ============================================================================

@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="cogence://knowledge-base/overview",
            name="AI Cogence Knowledge Base Overview",
            mimeType="text/plain",
            description="Overview of AI Cogence services and capabilities"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource"""
    if uri == "cogence://knowledge-base/overview":
        return """
AI Cogence Knowledge Base

Services:
- RAG Implementation: Advanced retrieval-augmented generation
- Fine-tuning: Custom AI model training
- AI Strategy Consulting: Expert guidance
- Trust & Security: Enterprise-grade security

Use the rag_query tool to ask specific questions about these services.
"""
    raise ValueError(f"Unknown resource: {uri}")


# ============================================================================
# Server Lifecycle
# ============================================================================

async def main():
    """Run the MCP server"""
    logger.info("=" * 60)
    logger.info("Starting AI Cogence MCP Tools Server")
    logger.info("=" * 60)
    
    # Initialize backend services (same as main.py)
    logger.info("Initializing backend services...")
    try:
        await init_db_pool()
        await init_langgraph()
        logger.info("✅ Backend services initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize backend: {e}", exc_info=True)
        sys.exit(1)
    
    # Run MCP server
    logger.info("🚀 MCP Tools Server ready")
    logger.info("Available tools: 7")
    logger.info("=" * 60)
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    finally:
        logger.info("Shutting down...")
        await cleanup()
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())

