"""
Pydantic Schemas for API Request/Response Validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a conversation"""
    title: Optional[str] = Field(None, max_length=200)
    llm_provider: str = Field(..., regex=r'^(openai|anthropic)$')
    model_name: str


class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    id: int
    user_id: int
    title: Optional[str]
    llm_provider: str
    model_name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    conversation_id: int
    role: str = Field(..., regex=r'^(user|assistant|system)$')
    content: str
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    conversation_id: int
    role: str
    content: str
    metadata: Optional[Dict[str, Any]]
    tokens_used: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    """Schema for SQL query request"""
    query: str = Field(..., min_length=1)
    user_id: Optional[int] = None


class QueryResponse(BaseModel):
    """Schema for query response"""
    columns: Optional[List[str]] = None
    rows: Optional[List[List[Any]]] = None
    row_count: Optional[int] = None
    message: Optional[str] = None
    rows_affected: Optional[int] = None
    execution_time: Optional[float] = None


class LLMChatRequest(BaseModel):
    """Schema for LLM chat request"""
    message: str = Field(..., min_length=1)
    provider: Optional[str] = Field(None, regex=r'^(openai|anthropic)$')
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    conversation_id: Optional[int] = None
    user_id: Optional[int] = None


class LLMChatResponse(BaseModel):
    """Schema for LLM chat response"""
    response: str
    provider: str
    model: str
    usage: Optional[Dict[str, int]] = None
    execution_time: Optional[float] = None


class SQLGenerationRequest(BaseModel):
    """Schema for SQL generation request"""
    natural_query: str = Field(..., min_length=1)
    table_context: Optional[str] = None
    provider: Optional[str] = Field(None, regex=r'^(openai|anthropic)$')
    user_id: Optional[int] = None


class DataAnalysisRequest(BaseModel):
    """Schema for data analysis request"""
    query: str = Field(..., min_length=1)
    analysis_request: str = Field(..., min_length=1)
    provider: Optional[str] = Field(None, regex=r'^(openai|anthropic)$')
    user_id: Optional[int] = None


class StatusResponse(BaseModel):
    """Schema for system status response"""
    database_connected: bool
    llm_providers: List[str]
    available_models: Dict[str, List[str]]
    mcp_session_id: str


class UsageStatsResponse(BaseModel):
    """Schema for usage statistics response"""
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    by_provider: Dict[str, Dict[str, int]]


class TokenRequest(BaseModel):
    """Schema for authentication token request"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int