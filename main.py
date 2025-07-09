#!/usr/bin/env python3
"""
Main Entry Point for MCP PostgreSQL LLM Server
"""

import asyncio
import logging
import typer
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler

from app.config import settings
from app.database import init_database, check_database_connection
from app.mcp_server import mcp_server

# Setup rich console and logging
console = Console()
logging.basicConfig(
    level=getattr(logging, settings.mcp_log_level),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)

app = typer.Typer(help="MCP PostgreSQL LLM Server")


@app.command()
def run_mcp_server():
    """Run the MCP server"""
    console.print("[bold green]Starting MCP PostgreSQL LLM Server...[/bold green]")
    
    # Check database connection
    if not check_database_connection():
        console.print("[bold red]❌ Cannot connect to PostgreSQL database[/bold red]")
        console.print(f"[yellow]Database URL: {settings.database_url}[/yellow]")
        raise typer.Exit(1)
    
    console.print("[bold green]✅ Database connection successful[/bold green]")
    
    # Initialize database tables
    try:
        init_database()
        console.print("[bold green]✅ Database tables initialized[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Database initialization failed: {e}[/bold red]")
        raise typer.Exit(1)
    
    # Run MCP server
    try:
        asyncio.run(mcp_server.run())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⚠️ Server stopped by user[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ Server error: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def run_web_server():
    """Run the web interface server"""
    import uvicorn
    from app.api.main import app as fastapi_app
    
    console.print("[bold green]Starting Web Interface Server...[/bold green]")
    console.print(f"[blue]Host: {settings.api_host}[/blue]")
    console.print(f"[blue]Port: {settings.api_port}[/blue]")
    console.print(f"[blue]Debug: {settings.debug}[/blue]")
    
    uvicorn.run(
        fastapi_app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.mcp_log_level.lower()
    )


@app.command()
def check_config():
    """Check configuration and system status"""
    console.print("[bold blue]Configuration Check[/bold blue]")
    console.print("=" * 50)
    
    # Database configuration
    console.print(f"[green]Database URL:[/green] {settings.database_url}")
    console.print(f"[green]Database Host:[/green] {settings.postgres_host}")
    console.print(f"[green]Database Port:[/green] {settings.postgres_port}")
    console.print(f"[green]Database Name:[/green] {settings.postgres_db}")
    
    # Test database connection
    if check_database_connection():
        console.print("[bold green]✅ Database connection: OK[/bold green]")
    else:
        console.print("[bold red]❌ Database connection: FAILED[/bold red]")
    
    # LLM API configuration
    console.print(f"\n[green]OpenAI API Key:[/green] {'✅ Configured' if settings.openai_api_key else '❌ Not configured'}")
    console.print(f"[green]Anthropic API Key:[/green] {'✅ Configured' if settings.anthropic_api_key else '❌ Not configured'}")
    
    # MCP Server configuration
    console.print(f"\n[green]MCP Server Host:[/green] {settings.mcp_server_host}")
    console.print(f"[green]MCP Server Port:[/green] {settings.mcp_server_port}")
    console.print(f"[green]Log Level:[/green] {settings.mcp_log_level}")
    
    # Web Server configuration
    console.print(f"\n[green]Web Server Host:[/green] {settings.api_host}")
    console.print(f"[green]Web Server Port:[/green] {settings.api_port}")
    console.print(f"[green]Debug Mode:[/green] {settings.debug}")


@app.command()
def init_db():
    """Initialize database tables"""
    console.print("[bold blue]Initializing Database...[/bold blue]")
    
    try:
        if not check_database_connection():
            console.print("[bold red]❌ Cannot connect to database[/bold red]")
            raise typer.Exit(1)
        
        init_database()
        console.print("[bold green]✅ Database tables initialized successfully[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Database initialization failed: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def create_user(
    username: str = typer.Option(..., help="Username for the new user"),
    email: str = typer.Option(..., help="Email for the new user"),
    password: str = typer.Option(..., help="Password for the new user"),
    full_name: Optional[str] = typer.Option(None, help="Full name for the new user"),
    admin: bool = typer.Option(False, help="Make user an admin")
):
    """Create a new user"""
    from app.database import get_db_context
    from app.api.auth import create_user as auth_create_user
    from app.models import User
    
    console.print(f"[bold blue]Creating user: {username}[/bold blue]")
    
    try:
        with get_db_context() as db:
            user = auth_create_user(db, username, email, password, full_name)
            
            if admin:
                user.is_admin = True
                db.commit()
                db.refresh(user)
            
            console.print(f"[bold green]✅ User created successfully[/bold green]")
            console.print(f"[green]ID:[/green] {user.id}")
            console.print(f"[green]Username:[/green] {user.username}")
            console.print(f"[green]Email:[/green] {user.email}")
            console.print(f"[green]Admin:[/green] {user.is_admin}")
            
    except Exception as e:
        console.print(f"[bold red]❌ User creation failed: {e}[/bold red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()