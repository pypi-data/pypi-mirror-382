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
import time
from collections import defaultdict

# Add backend to path to import existing services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.db import init_db_pool, cleanup, db_pool, embeddings
from controllers.chat_controller import response_generation, init_langgraph
from controllers.s3_controller import fetch_and_chunk_s3_docs
from models.chat_model import ChatRequest
import httpx  # For calling existing API endpoints

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-cogence-tools")

# Load environment
load_dotenv()

# API Base URL for existing backend services
API_BASE_URL = os.getenv("API_BASE_URL", "http://54.241.32.247:5026")

# ============================================================================
# Rate Limiting for Website Tools (Polite Usage)
# ============================================================================

class PoliteRateLimiter:
    """
    Polite rate limiter for Cogence website tools.
    Ensures fair usage of the hosted API.
    """
    def __init__(self, 
                 min_delay_seconds: float = 1.0,  # Min 1 second between requests
                 max_requests_per_minute: int = 20):  # Max 20 requests per minute
        self.min_delay = min_delay_seconds
        self.max_rpm = max_requests_per_minute
        self.last_request_time = defaultdict(float)
        self.request_timestamps = defaultdict(list)
    
    async def wait_if_needed(self, tool_name: str):
        """
        Wait if necessary to respect rate limits.
        Implements both minimum delay and requests-per-minute limit.
        """
        current_time = time.time()
        
        # Check minimum delay since last request
        last_time = self.last_request_time[tool_name]
        time_since_last = current_time - last_time
        
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            logger.info(f"⏱️  Rate limit: waiting {wait_time:.2f}s before {tool_name}")
            await asyncio.sleep(wait_time)
            current_time = time.time()
        
        # Check requests per minute limit
        timestamps = self.request_timestamps[tool_name]
        # Remove timestamps older than 1 minute
        cutoff_time = current_time - 60
        timestamps[:] = [ts for ts in timestamps if ts > cutoff_time]
        
        if len(timestamps) >= self.max_rpm:
            # Wait until the oldest request is more than 1 minute old
            oldest_time = timestamps[0]
            wait_time = 60 - (current_time - oldest_time)
            if wait_time > 0:
                logger.info(f"⏱️  Rate limit: max {self.max_rpm} requests/min reached for {tool_name}, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                current_time = time.time()
        
        # Record this request
        self.last_request_time[tool_name] = current_time
        self.request_timestamps[tool_name].append(current_time)
        logger.debug(f"✅ Rate limit check passed for {tool_name}")

# Initialize rate limiter for website tools
website_rate_limiter = PoliteRateLimiter(
    min_delay_seconds=1.0,  # 1 second between requests
    max_requests_per_minute=20  # Max 20 requests per minute
)

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
    ),
    Tool(
        name="site_search",
        description="Search across Cogence.ai website pages including Industries, Partnerships, Trust & Security, About Us, AI Strategy, RAG Implementation, Fine-tuning, and more. Uses semantic vector search to find relevant content.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant content on cogence.ai"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_page",
        description="Get cleaned content from a specific Cogence.ai page URL (e.g., /home, /about-us, /ai-strategy-consulting, /partnerships, /trust-security, /rag-implementation, /fine-tuning, /contact-us). Returns the full text content of the page.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Page URL path (e.g., '/about-us', '/partnerships', '/home')"
                }
            },
            "required": ["url"]
        }
    ),
    Tool(
        name="extract_sections",
        description="Extract specific sections from a Cogence.ai page like headings, summaries, CTAs (calls-to-action), key points, or service descriptions. Useful for getting structured information from pages.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Page URL path (e.g., '/ai-strategy-consulting', '/partnerships')"
                },
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["headings", "summary", "cta", "key_points", "services", "all"]
                    },
                    "description": "Sections to extract: headings, summary, cta, key_points, services, or all"
                }
            },
            "required": ["url", "sections"]
        }
    ),
    Tool(
        name="get_sitemap",
        description="Get a sitemap of all available pages on Cogence.ai. Returns a list of all page URLs, titles, and descriptions. Useful for discovering what content is available.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain to get sitemap for (default: cogence.ai)",
                    "default": "cogence.ai"
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
        elif name == "site_search":
            return await handle_site_search(arguments)
        elif name == "get_page":
            return await handle_get_page(arguments)
        elif name == "extract_sections":
            return await handle_extract_sections(arguments)
        elif name == "get_sitemap":
            return await handle_get_sitemap(arguments)
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


async def handle_site_search(arguments: dict) -> Sequence[TextContent]:
    """Search across Cogence.ai website pages using existing chat API"""
    query = arguments.get("query")
    limit = arguments.get("limit", 5)
    
    if not query:
        return [TextContent(type="text", text="Error: query is required")]
    
    # Apply rate limiting for polite API usage
    await website_rate_limiter.wait_if_needed("site_search")
    
    try:
        logger.info(f"Searching cogence.ai for: {query}")
        
        # Use existing chat endpoint with cogence-website domain
        session_id = "website-search-session"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Call the streaming chat endpoint
            response = await client.post(
                f"{API_BASE_URL}/chat/{session_id}",
                json={
                    "user_query": query,
                    "domain": "cogence-website",
                    "content_type": "search"
                }
            )
            response.raise_for_status()
            
            # Parse streaming response
            results = []
            sources = []
            
            for line in response.text.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("type") == "final" and "sources" in data:
                            sources = data["sources"][:limit]
                            break
                    except:
                        continue
            
            # Format results
            for source in sources:
                results.append({
                    "content": source.get("content", ""),
                    "title": source.get("metadata", {}).get("title", "Unknown"),
                    "url": source.get("metadata", {}).get("url", "Unknown"),
                    "source": source.get("metadata", {}).get("source", "Unknown"),
                    "relevance_score": source.get("similarity", None)
                })
            
            result_data = {
                "query": query,
                "results_count": len(results),
                "results": results
            }
        
        import json
        return [TextContent(type="text", text=json.dumps(result_data, indent=2))]
        
    except Exception as e:
        logger.error(f"Error in site_search: {e}", exc_info=True)
        import json
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "api_url": f"{API_BASE_URL}/chat/{{session_id}}"
        }, indent=2))]


async def handle_get_page(arguments: dict) -> Sequence[TextContent]:
    """Get content from a specific Cogence.ai page using existing chat API"""
    url = arguments.get("url")
    
    if not url:
        return [TextContent(type="text", text="Error: url is required")]
    
    # Apply rate limiting for polite API usage
    await website_rate_limiter.wait_if_needed("get_page")
    
    try:
        logger.info(f"Getting page content for: {url}")
        
        # Normalize URL
        url_normalized = url.strip("/")
        
        # Use existing chat endpoint
        session_id = "website-page-session"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/chat/{session_id}",
                json={
                    "user_query": f"get full content of {url_normalized} page",
                    "domain": "cogence-website",
                    "content_type": "page"
                }
            )
            response.raise_for_status()
            
            # Parse streaming response
            sources = []
            for line in response.text.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("type") == "final" and "sources" in data:
                            sources = data["sources"]
                            break
                    except:
                        continue
            
            # Extract page content
            if sources and len(sources) > 0:
                source = sources[0]
                result_data = {
                    "url": url,
                    "title": source.get("metadata", {}).get("title", "Unknown"),
                    "content": source.get("content", ""),
                    "metadata": {
                        "source": source.get("metadata", {}).get("source", "Unknown"),
                        "url": source.get("metadata", {}).get("url", url)
                    }
                }
            else:
                result_data = {
                    "url": url,
                    "error": "Page not found",
                    "available_pages": ["home", "about-us", "ai-strategy-consulting", "partnerships", 
                                       "trust-security", "rag-implementation", "fine-tuning", "contact-us"]
                }
        
        import json
        return [TextContent(type="text", text=json.dumps(result_data, indent=2))]
        
    except Exception as e:
        logger.error(f"Error in get_page: {e}", exc_info=True)
        import json
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "api_url": f"{API_BASE_URL}/chat/{{session_id}}"
        }, indent=2))]


async def handle_extract_sections(arguments: dict) -> Sequence[TextContent]:
    """Extract specific sections from a Cogence.ai page using existing chat API"""
    url = arguments.get("url")
    sections = arguments.get("sections", ["all"])
    
    if not url:
        return [TextContent(type="text", text="Error: url is required")]
    
    # Apply rate limiting for polite API usage
    await website_rate_limiter.wait_if_needed("extract_sections")
    
    try:
        logger.info(f"Extracting sections from: {url}")
        
        # Get page content via API
        url_normalized = url.strip("/")
        session_id = "website-extract-session"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/chat/{session_id}",
                json={
                    "user_query": f"get full content of {url_normalized} page",
                    "domain": "cogence-website",
                    "content_type": "page"
                }
            )
            response.raise_for_status()
            
            # Parse streaming response
            sources = []
            for line in response.text.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("type") == "final" and "sources" in data:
                            sources = data["sources"]
                            break
                    except:
                        continue
            
            if sources and len(sources) > 0:
                source = sources[0]
                content = source.get("content", "")
                
                extracted = {
                    "url": url,
                    "title": source.get("metadata", {}).get("title", "Unknown")
                }
                
                # Extract requested sections
                if "all" in sections or "headings" in sections:
                    headings = [line.strip() for line in content.split("\n") if line.strip().startswith("#")]
                    extracted["headings"] = headings
                
                if "all" in sections or "summary" in sections:
                    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.strip().startswith("#")]
                    extracted["summary"] = paragraphs[0] if paragraphs else ""
                
                if "all" in sections or "cta" in sections:
                    cta_keywords = ["contact", "get started", "learn more", "schedule", "book", "demo"]
                    ctas = []
                    for line in content.split("\n"):
                        if any(keyword in line.lower() for keyword in cta_keywords):
                            ctas.append(line.strip())
                    extracted["cta"] = ctas
                
                if "all" in sections or "key_points" in sections:
                    key_points = [line.strip("- ").strip() for line in content.split("\n") if line.strip().startswith("- ")]
                    extracted["key_points"] = key_points
                
                if "all" in sections or "services" in sections:
                    service_lines = []
                    for line in content.split("\n"):
                        if any(word in line.lower() for word in ["service", "offering", "solution", "capability"]):
                            service_lines.append(line.strip())
                    extracted["services"] = service_lines
                
                result_data = extracted
            else:
                result_data = {
                    "url": url,
                    "error": "Page not found"
                }
        
        import json
        return [TextContent(type="text", text=json.dumps(result_data, indent=2))]
        
    except Exception as e:
        logger.error(f"Error in extract_sections: {e}", exc_info=True)
        import json
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "api_url": f"{API_BASE_URL}/chat/{{session_id}}"
        }, indent=2))]


async def handle_get_sitemap(arguments: dict) -> Sequence[TextContent]:
    """Get sitemap of all available pages on Cogence.ai using existing API"""
    domain = arguments.get("domain", "cogence.ai")
    
    # Apply rate limiting for polite API usage
    await website_rate_limiter.wait_if_needed("get_sitemap")
    
    try:
        logger.info(f"Getting sitemap for: {domain}")
        
        # Call existing website loader status API to get available pages
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{API_BASE_URL}/api/website-loader/status")
            response.raise_for_status()
            data = response.json()
            
            # Extract available content files from status response
            if "available_content_files" in data:
                pages = []
                for file_info in data["available_content_files"]:
                    # Parse format: "home.md (/)"
                    parts = file_info.split(" (")
                    if len(parts) == 2:
                        filename = parts[0].replace(".md", "")
                        url_path = parts[1].rstrip(")")
                        
                        pages.append({
                            "url": url_path,
                            "path": filename,
                            "title": filename.replace("-", " ").title(),
                            "description": f"{filename.replace('-', ' ').title()} page content"
                        })
                
                sitemap = {
                    "domain": domain,
                    "base_url": f"https://{domain}",
                    "pages": pages,
                    "total_pages": len(pages),
                    "api_status": data.get("database", "Unknown")
                }
            else:
                # Fallback to hardcoded sitemap
                sitemap = {
                    "domain": domain,
                    "base_url": f"https://{domain}",
                    "pages": [
                        {"url": "/", "path": "home", "title": "Home", "description": "AI consulting and implementation services"},
                        {"url": "/about-us", "path": "about-us", "title": "About Us", "description": "Learn about AI Cogence team and mission"},
                        {"url": "/ai-strategy-consulting", "path": "ai-strategy-consulting", "title": "AI Strategy Consulting", "description": "Strategic AI consulting services"},
                        {"url": "/rag-implementation", "path": "rag-implementation", "title": "RAG Implementation", "description": "RAG implementation services"},
                        {"url": "/fine-tuning", "path": "fine-tuning", "title": "Fine-tuning", "description": "AI model fine-tuning"},
                        {"url": "/partnerships", "path": "partnerships", "title": "Partnerships", "description": "Partner with AI Cogence"},
                        {"url": "/trust-security", "path": "trust-security", "title": "Trust & Security", "description": "Security commitment"},
                        {"url": "/contact-us", "path": "contact-us", "title": "Contact Us", "description": "Get in touch"}
                    ],
                    "total_pages": 8
                }
        
        import json
        return [TextContent(type="text", text=json.dumps(sitemap, indent=2))]
        
    except Exception as e:
        logger.error(f"Error in get_sitemap: {e}", exc_info=True)
        import json
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "api_url": f"{API_BASE_URL}/api/website-loader/status"
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
    logger.info("Available tools: 11")  # 7 original + 4 website tools
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

