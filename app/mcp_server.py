"""
MCP Server Implementation with PostgreSQL and LLM Integration
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from mcp import Server, stdio_server
from mcp.types import (
    Resource, Tool, CallToolResult, GetResourceResult,
    ListResourcesResult, ListToolsResult
)
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db_context, check_database_connection
from app.models import QueryHistory, User, Conversation, Message, APIUsage
from app.llm.manager import llm_manager
from app.config import settings

logger = logging.getLogger(__name__)


class MCPDatabaseServer:
    """MCP Server with PostgreSQL and LLM integration"""
    
    def __init__(self):
        self.server = Server("postgresql-llm-mcp-server")
        self.session_id = str(uuid.uuid4())
        self.setup_handlers()
        
        # Check database connection on startup
        if not check_database_connection():
            raise RuntimeError("Cannot connect to PostgreSQL database")
        
        logger.info(f"MCP Server initialized with session ID: {self.session_id}")
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> ListResourcesResult:
            """List available resources"""
            resources = [
                Resource(
                    uri="postgresql://tables",
                    name="Database Tables",
                    description="List all tables in the PostgreSQL database",
                    mimeType="application/json"
                ),
                Resource(
                    uri="postgresql://schema",
                    name="Database Schema",
                    description="Get database schema information",
                    mimeType="application/json"
                ),
                Resource(
                    uri="llm://models",
                    name="Available LLM Models",
                    description="List all available LLM models from configured providers",
                    mimeType="application/json"
                ),
                Resource(
                    uri="mcp://status",
                    name="MCP Server Status",
                    description="Get current server status and configuration",
                    mimeType="application/json"
                )
            ]
            return ListResourcesResult(resources=resources)
        
        @self.server.get_resource()
        async def get_resource(uri: str) -> GetResourceResult:
            """Get resource content"""
            
            if uri == "postgresql://tables":
                return await self._get_database_tables()
            elif uri == "postgresql://schema":
                return await self._get_database_schema()
            elif uri == "llm://models":
                return await self._get_llm_models()
            elif uri == "mcp://status":
                return await self._get_server_status()
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools"""
            tools = [
                Tool(
                    name="execute_sql",
                    description="Execute SQL query on PostgreSQL database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute"
                            },
                            "user_id": {
                                "type": "integer",
                                "description": "User ID for tracking (optional)"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="chat_with_llm",
                    description="Chat with configured LLM providers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to send to the LLM"
                            },
                            "provider": {
                                "type": "string",
                                "description": "LLM provider (openai/anthropic). Auto-select if not specified"
                            },
                            "model": {
                                "type": "string",
                                "description": "Model to use. Auto-select if not specified"
                            },
                            "system_prompt": {
                                "type": "string",
                                "description": "System prompt for the conversation"
                            },
                            "conversation_id": {
                                "type": "integer",
                                "description": "Conversation ID for tracking"
                            },
                            "user_id": {
                                "type": "integer",
                                "description": "User ID for tracking"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="sql_with_llm",
                    description="Generate and execute SQL queries using LLM assistance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "natural_language_query": {
                                "type": "string",
                                "description": "Natural language description of what you want to query"
                            },
                            "table_context": {
                                "type": "string",
                                "description": "Additional context about tables and relationships"
                            },
                            "provider": {
                                "type": "string",
                                "description": "LLM provider to use for SQL generation"
                            },
                            "user_id": {
                                "type": "integer",
                                "description": "User ID for tracking"
                            }
                        },
                        "required": ["natural_language_query"]
                    }
                ),
                Tool(
                    name="analyze_data",
                    description="Analyze database query results using LLM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute and analyze"
                            },
                            "analysis_request": {
                                "type": "string",
                                "description": "What type of analysis you want (trends, insights, summary, etc.)"
                            },
                            "provider": {
                                "type": "string",
                                "description": "LLM provider to use for analysis"
                            },
                            "user_id": {
                                "type": "integer",
                                "description": "User ID for tracking"
                            }
                        },
                        "required": ["query", "analysis_request"]
                    }
                )
            ]
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            
            try:
                if name == "execute_sql":
                    return await self._execute_sql(arguments)
                elif name == "chat_with_llm":
                    return await self._chat_with_llm(arguments)
                elif name == "sql_with_llm":
                    return await self._sql_with_llm(arguments)
                elif name == "analyze_data":
                    return await self._analyze_data(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return CallToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Error executing tool '{name}': {str(e)}"
                    }],
                    isError=True
                )
    
    async def _get_database_tables(self) -> GetResourceResult:
        """Get list of database tables"""
        try:
            with get_db_context() as db:
                result = db.execute(text("""
                    SELECT table_name, table_type 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                
                tables = [{"name": row[0], "type": row[1]} for row in result.fetchall()]
                
                return GetResourceResult(
                    contents=[{
                        "type": "text",
                        "text": json.dumps(tables, indent=2)
                    }]
                )
        except Exception as e:
            logger.error(f"Error getting database tables: {e}")
            raise
    
    async def _get_database_schema(self) -> GetResourceResult:
        """Get database schema information"""
        try:
            with get_db_context() as db:
                result = db.execute(text("""
                    SELECT 
                        table_name,
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position
                """))
                
                schema = {}
                for row in result.fetchall():
                    table_name = row[0]
                    if table_name not in schema:
                        schema[table_name] = []
                    
                    schema[table_name].append({
                        "column": row[1],
                        "type": row[2],
                        "nullable": row[3] == "YES",
                        "default": row[4]
                    })
                
                return GetResourceResult(
                    contents=[{
                        "type": "text",
                        "text": json.dumps(schema, indent=2)
                    }]
                )
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            raise
    
    async def _get_llm_models(self) -> GetResourceResult:
        """Get available LLM models"""
        try:
            models = llm_manager.get_available_models()
            providers = llm_manager.get_available_providers()
            
            info = {
                "providers": providers,
                "models_by_provider": models,
                "default_provider": llm_manager.get_default_provider()
            }
            
            return GetResourceResult(
                contents=[{
                    "type": "text",
                    "text": json.dumps(info, indent=2)
                }]
            )
        except Exception as e:
            logger.error(f"Error getting LLM models: {e}")
            raise
    
    async def _get_server_status(self) -> GetResourceResult:
        """Get server status"""
        try:
            status = {
                "session_id": self.session_id,
                "database_connected": check_database_connection(),
                "llm_providers": llm_manager.get_available_providers(),
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            return GetResourceResult(
                contents=[{
                    "type": "text",
                    "text": json.dumps(status, indent=2)
                }]
            )
        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            raise
    
    async def _execute_sql(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute SQL query"""
        query = arguments.get("query")
        user_id = arguments.get("user_id")
        
        if not query:
            raise ValueError("Query is required")
        
        start_time = datetime.now()
        
        try:
            with get_db_context() as db:
                result = db.execute(text(query))
                
                # Handle different types of queries
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = list(result.keys())
                    
                    data = {
                        "columns": columns,
                        "rows": [list(row) for row in rows],
                        "row_count": len(rows)
                    }
                else:
                    data = {
                        "message": "Query executed successfully",
                        "rows_affected": result.rowcount
                    }
                
                # Log query execution
                if user_id:
                    await self._log_query_execution(
                        user_id, query, True, len(rows) if result.returns_rows else result.rowcount,
                        start_time
                    )
                
                return CallToolResult(
                    content=[{
                        "type": "text",
                        "text": json.dumps(data, indent=2, default=str)
                    }]
                )
                
        except Exception as e:
            # Log failed query execution
            if user_id:
                await self._log_query_execution(
                    user_id, query, False, 0, start_time, str(e)
                )
            raise
    
    async def _chat_with_llm(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Chat with LLM"""
        message = arguments.get("message")
        provider = arguments.get("provider")
        model = arguments.get("model")
        system_prompt = arguments.get("system_prompt")
        conversation_id = arguments.get("conversation_id")
        user_id = arguments.get("user_id")
        
        if not message:
            raise ValueError("Message is required")
        
        try:
            response = await llm_manager.chat_completion(
                user_message=message,
                provider_name=provider,
                model=model,
                system_prompt=system_prompt
            )
            
            # Log the conversation if user_id is provided
            if user_id:
                await self._log_llm_usage(user_id, response)
            
            return CallToolResult(
                content=[{
                    "type": "text",
                    "text": response["content"]
                }]
            )
            
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            raise
    
    async def _sql_with_llm(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Generate and execute SQL using LLM"""
        natural_query = arguments.get("natural_language_query")
        table_context = arguments.get("table_context", "")
        provider = arguments.get("provider")
        user_id = arguments.get("user_id")
        
        if not natural_query:
            raise ValueError("Natural language query is required")
        
        try:
            # Get database schema for context
            schema_resource = await self._get_database_schema()
            schema_text = schema_resource.contents[0]["text"]
            
            # Create system prompt for SQL generation
            system_prompt = f"""
            You are a PostgreSQL expert. Generate SQL queries based on natural language requests.
            
            Database Schema:
            {schema_text}
            
            Additional Context:
            {table_context}
            
            Rules:
            1. Only generate SELECT queries for safety
            2. Use proper PostgreSQL syntax
            3. Include only the SQL query in your response, no explanations
            4. Ensure the query is safe and won't cause performance issues
            """
            
            # Generate SQL using LLM
            sql_response = await llm_manager.chat_completion(
                user_message=f"Generate SQL query for: {natural_query}",
                provider_name=provider,
                system_prompt=system_prompt
            )
            
            generated_sql = sql_response["content"].strip()
            
            # Execute the generated SQL
            execution_result = await self._execute_sql({
                "query": generated_sql,
                "user_id": user_id
            })
            
            result = {
                "natural_language_query": natural_query,
                "generated_sql": generated_sql,
                "execution_result": json.loads(execution_result.content[0]["text"])
            }
            
            return CallToolResult(
                content=[{
                    "type": "text",
                    "text": json.dumps(result, indent=2, default=str)
                }]
            )
            
        except Exception as e:
            logger.error(f"SQL generation with LLM error: {e}")
            raise
    
    async def _analyze_data(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Analyze database query results using LLM"""
        query = arguments.get("query")
        analysis_request = arguments.get("analysis_request")
        provider = arguments.get("provider")
        user_id = arguments.get("user_id")
        
        if not query or not analysis_request:
            raise ValueError("Both query and analysis_request are required")
        
        try:
            # Execute the query first
            query_result = await self._execute_sql({
                "query": query,
                "user_id": user_id
            })
            
            query_data = json.loads(query_result.content[0]["text"])
            
            # Create analysis prompt
            system_prompt = """
            You are a data analyst. Analyze the provided query results and provide insights.
            Present your analysis in a clear, structured format with:
            1. Summary of the data
            2. Key insights and patterns
            3. Recommendations if applicable
            """
            
            analysis_prompt = f"""
            SQL Query: {query}
            
            Query Results: {json.dumps(query_data, indent=2, default=str)}
            
            Analysis Request: {analysis_request}
            
            Please provide a detailed analysis of this data.
            """
            
            # Get analysis from LLM
            analysis_response = await llm_manager.chat_completion(
                user_message=analysis_prompt,
                provider_name=provider,
                system_prompt=system_prompt
            )
            
            result = {
                "query": query,
                "data": query_data,
                "analysis_request": analysis_request,
                "analysis": analysis_response["content"]
            }
            
            return CallToolResult(
                content=[{
                    "type": "text",
                    "text": json.dumps(result, indent=2, default=str)
                }]
            )
            
        except Exception as e:
            logger.error(f"Data analysis error: {e}")
            raise
    
    async def _log_query_execution(
        self,
        user_id: int,
        query: str,
        success: bool,
        result_count: int,
        start_time: datetime,
        error_message: Optional[str] = None
    ):
        """Log query execution to database"""
        try:
            with get_db_context() as db:
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                query_log = QueryHistory(
                    user_id=user_id,
                    query_text=query,
                    query_type=query.strip().split()[0].upper(),
                    execution_time=int(execution_time),
                    success=success,
                    error_message=error_message,
                    result_count=result_count
                )
                
                db.add(query_log)
                
        except Exception as e:
            logger.error(f"Failed to log query execution: {e}")
    
    async def _log_llm_usage(self, user_id: int, response: Dict[str, Any]):
        """Log LLM usage to database"""
        try:
            with get_db_context() as db:
                usage = response.get("usage", {})
                
                api_usage = APIUsage(
                    user_id=user_id,
                    provider=response.get("provider", "unknown"),
                    model=response.get("model", "unknown"),
                    tokens_input=usage.get("prompt_tokens", 0),
                    tokens_output=usage.get("completion_tokens", 0)
                )
                
                db.add(api_usage)
                
        except Exception as e:
            logger.error(f"Failed to log LLM usage: {e}")
    
    async def run(self):
        """Run the MCP server"""
        logger.info(f"Starting MCP Server on {settings.mcp_server_host}:{settings.mcp_server_port}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                options={"debug": settings.debug}
            )


# Global server instance
mcp_server = MCPDatabaseServer()