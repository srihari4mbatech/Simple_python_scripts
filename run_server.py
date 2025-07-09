#!/usr/bin/env python3
"""
Run both MCP Server and Web Interface
"""

import asyncio
import multiprocessing
import signal
import sys
import time
from rich.console import Console

from main import run_web_server
from app.config import settings

console = Console()


def run_mcp_server_process():
    """Run MCP server in a separate process"""
    import subprocess
    import sys
    
    try:
        # Run MCP server using the main.py script
        subprocess.run([sys.executable, "main.py", "run-mcp-server"])
    except KeyboardInterrupt:
        pass


def run_web_server_process():
    """Run web server in a separate process"""
    try:
        run_web_server()
    except KeyboardInterrupt:
        pass


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    console.print("\n[bold yellow]⚠️ Shutting down servers...[/bold yellow]")
    sys.exit(0)


def main():
    """Main function to run both servers"""
    console.print("[bold green]🚀 Starting MCP PostgreSQL LLM Server Application[/bold green]")
    console.print("=" * 60)
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create processes for both servers
    mcp_process = multiprocessing.Process(target=run_mcp_server_process, name="MCP-Server")
    web_process = multiprocessing.Process(target=run_web_server_process, name="Web-Server")
    
    try:
        # Start both processes
        console.print("[blue]Starting MCP Server process...[/blue]")
        mcp_process.start()
        
        # Wait a moment for MCP server to initialize
        time.sleep(2)
        
        console.print("[blue]Starting Web Interface process...[/blue]")
        web_process.start()
        
        console.print("\n[bold green]✅ Both servers are running![/bold green]")
        console.print(f"[green]🌐 Web Interface:[/green] http://{settings.api_host}:{settings.api_port}")
        console.print(f"[green]🔧 MCP Server:[/green] {settings.mcp_server_host}:{settings.mcp_server_port}")
        console.print("\n[yellow]Press Ctrl+C to stop all servers[/yellow]")
        
        # Wait for processes to complete
        mcp_process.join()
        web_process.join()
        
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⚠️ Shutting down...[/bold yellow]")
    
    finally:
        # Terminate processes if they're still running
        if mcp_process.is_alive():
            console.print("[blue]Stopping MCP Server...[/blue]")
            mcp_process.terminate()
            mcp_process.join(timeout=5)
            if mcp_process.is_alive():
                mcp_process.kill()
        
        if web_process.is_alive():
            console.print("[blue]Stopping Web Server...[/blue]")
            web_process.terminate()
            web_process.join(timeout=5)
            if web_process.is_alive():
                web_process.kill()
        
        console.print("[bold green]✅ All servers stopped[/bold green]")


if __name__ == "__main__":
    main()