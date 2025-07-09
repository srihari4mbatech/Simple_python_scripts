"""
FastAPI Backend for MCP Server Web Interface
"""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db, init_database, check_database_connection
from app.models import User, Conversation, Message, QueryHistory, APIUsage
from app.llm.manager import llm_manager
from app.mcp_server import mcp_server
from app.config import settings
from .schemas import (
    UserCreate, UserResponse, ConversationCreate, ConversationResponse,
    MessageCreate, MessageResponse, QueryRequest, QueryResponse,
    LLMChatRequest, LLMChatResponse
)
from .auth import get_current_user, create_access_token

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP PostgreSQL LLM Server",
    description="Web interface for MCP server with PostgreSQL and LLM integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and check connections"""
    logger.info("Starting FastAPI application...")
    
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    if not check_database_connection():
        logger.error("Database connection failed")
        raise RuntimeError("Cannot connect to database")
    
    logger.info("FastAPI application started successfully")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database_connected": check_database_connection(),
        "llm_providers": llm_manager.get_available_providers(),
        "mcp_session": mcp_server.session_id
    }


# Main web interface
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main web interface"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "MCP PostgreSQL LLM Server"
    })


# API Endpoints

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "database_connected": check_database_connection(),
        "llm_providers": llm_manager.get_available_providers(),
        "available_models": llm_manager.get_available_models(),
        "mcp_session_id": mcp_server.session_id
    }


@app.get("/api/database/tables")
async def get_database_tables(db: Session = Depends(get_db)):
    """Get list of database tables"""
    try:
        tables_resource = await mcp_server._get_database_tables()
        return JSONResponse(content=tables_resource.contents[0]["text"])
    except Exception as e:
        logger.error(f"Error getting database tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/database/schema")
async def get_database_schema(db: Session = Depends(get_db)):
    """Get database schema"""
    try:
        schema_resource = await mcp_server._get_database_schema()
        return JSONResponse(content=schema_resource.contents[0]["text"])
    except Exception as e:
        logger.error(f"Error getting database schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/database/query")
async def execute_query(
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Execute SQL query"""
    try:
        result = await mcp_server._execute_sql({
            "query": query_request.query,
            "user_id": query_request.user_id
        })
        
        return JSONResponse(content=result.content[0]["text"])
        
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm/chat")
async def chat_with_llm(
    chat_request: LLMChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with LLM"""
    try:
        result = await mcp_server._chat_with_llm({
            "message": chat_request.message,
            "provider": chat_request.provider,
            "model": chat_request.model,
            "system_prompt": chat_request.system_prompt,
            "user_id": chat_request.user_id
        })
        
        return {"response": result.content[0]["text"]}
        
    except Exception as e:
        logger.error(f"LLM chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm/sql-generate")
async def generate_sql(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Generate and execute SQL using LLM"""
    try:
        result = await mcp_server._sql_with_llm({
            "natural_language_query": request.get("natural_query"),
            "table_context": request.get("table_context", ""),
            "provider": request.get("provider"),
            "user_id": request.get("user_id")
        })
        
        return JSONResponse(content=result.content[0]["text"])
        
    except Exception as e:
        logger.error(f"SQL generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm/analyze")
async def analyze_data(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Analyze data using LLM"""
    try:
        result = await mcp_server._analyze_data({
            "query": request.get("query"),
            "analysis_request": request.get("analysis_request"),
            "provider": request.get("provider"),
            "user_id": request.get("user_id")
        })
        
        return JSONResponse(content=result.content[0]["text"])
        
    except Exception as e:
        logger.error(f"Data analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversations")
async def get_conversations(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get user conversations"""
    query = db.query(Conversation)
    if user_id:
        query = query.filter(Conversation.user_id == user_id)
    
    conversations = query.order_by(Conversation.created_at.desc()).limit(50).all()
    return [
        {
            "id": conv.id,
            "title": conv.title,
            "llm_provider": conv.llm_provider,
            "model_name": conv.model_name,
            "created_at": conv.created_at.isoformat(),
            "message_count": len(conv.messages)
        }
        for conv in conversations
    ]


@app.get("/api/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get messages for a conversation"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
            "tokens_used": msg.tokens_used
        }
        for msg in messages
    ]


@app.get("/api/query-history")
async def get_query_history(
    user_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get query execution history"""
    query = db.query(QueryHistory)
    if user_id:
        query = query.filter(QueryHistory.user_id == user_id)
    
    history = query.order_by(QueryHistory.created_at.desc()).limit(limit).all()
    return [
        {
            "id": q.id,
            "query_text": q.query_text,
            "query_type": q.query_type,
            "execution_time": q.execution_time,
            "success": q.success,
            "result_count": q.result_count,
            "created_at": q.created_at.isoformat(),
            "error_message": q.error_message
        }
        for q in history
    ]


@app.get("/api/usage-stats")
async def get_usage_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get API usage statistics"""
    query = db.query(APIUsage)
    if user_id:
        query = query.filter(APIUsage.user_id == user_id)
    
    usage = query.order_by(APIUsage.request_time.desc()).limit(100).all()
    
    # Aggregate statistics
    stats = {
        "total_requests": len(usage),
        "total_input_tokens": sum(u.tokens_input for u in usage),
        "total_output_tokens": sum(u.tokens_output for u in usage),
        "by_provider": {}
    }
    
    for u in usage:
        if u.provider not in stats["by_provider"]:
            stats["by_provider"][u.provider] = {
                "requests": 0,
                "input_tokens": 0,
                "output_tokens": 0
            }
        
        stats["by_provider"][u.provider]["requests"] += 1
        stats["by_provider"][u.provider]["input_tokens"] += u.tokens_input
        stats["by_provider"][u.provider]["output_tokens"] += u.tokens_output
    
    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )