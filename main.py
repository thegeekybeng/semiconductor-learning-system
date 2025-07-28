"""
Semiconductor Manufacturing Self-Learning Module
Main entry point for the application
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.table import Table
except ImportError:
    typer = None
    Console = None
    Table = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure basic logging
logging.basicConfig(level=logging.INFO)

from core.config import Config
from core.database import DatabaseManager
from schedulers.main_scheduler import MainScheduler
from api.server import create_app
from scripts.init_system import initialize_system

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Create console and app only if dependencies are available
if typer and Console:
    app = typer.Typer(help="Semiconductor Manufacturing Self-Learning Module")
    console = Console()
else:
    app = None
    console = None

def safe_console_print(message: str, style: str = ""):
    """Safe console printing that works even without rich"""
    if console:
        console.print(f"[{style}]{message}[/{style}]" if style else message)
    else:
        print(message)

def create_table(title: str):
    """Create a table if rich is available, otherwise return None"""
    if Table:
        return Table(title=title)
    else:
        return None

if app:
    @app.command()
    def init(
        force: bool = typer.Option(False, "--force", "-f", help="Force re-initialization")
    ):
        """Initialize the system database and configuration."""
        safe_console_print("Initializing Semiconductor Learning System...", "bold blue")
        
        try:
            success = initialize_system(force=force)
            if success:
                safe_console_print("✓ System initialized successfully!", "bold green")
            else:
                safe_console_print("✗ System initialization failed!", "bold red")
                raise typer.Exit(1)
        except Exception as e:
            safe_console_print(f"Error during initialization: {e}", "bold red")
            raise typer.Exit(1)

@app.command()
def crawl(
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Specific source to crawl"),
    update_existing: bool = typer.Option(False, "--update", "-u", help="Update existing data")
):
    """Start manual crawling process."""
    console.print("[bold blue]Starting crawling process...[/bold blue]")
    
    from crawlers.crawler_manager import CrawlerManager
    
    async def run_crawl():
        crawler_manager = CrawlerManager()
        await crawler_manager.crawl_sources(source_filter=source, update_existing=update_existing)
    
    asyncio.run(run_crawl())
    console.print("[bold green]✓ Crawling completed![/bold green]")

@app.command()
def query(
    question: str = typer.Argument(..., help="Question to ask the system"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed response")
):
    """Query the knowledge base."""
    from rag.query_engine import QueryEngine
    
    query_engine = QueryEngine()
    response = query_engine.query(question, include_sources=detailed)
    
    console.print(f"\n[bold blue]Question:[/bold blue] {question}")
    console.print(f"[bold green]Answer:[/bold green] {response.answer}")
    
    if detailed and response.sources:
        table = Table(title="Sources")
        table.add_column("Source", style="cyan")
        table.add_column("Relevance", style="magenta")
        table.add_column("Snippet", style="white")
        
        for source in response.sources[:5]:
            table.add_row(
                source.source_url or "Unknown",
                f"{source.relevance_score:.2f}",
                source.text[:100] + "..." if len(source.text) > 100 else source.text
            )
        
        console.print(table)

@app.command()
def scheduler(
    mode: str = typer.Option("start", "--mode", "-m", help="Scheduler mode: start, stop, status"),
    daemon: bool = typer.Option(False, "--daemon", "-d", help="Run as daemon")
):
    """Manage the automated scheduler."""
    scheduler_manager = MainScheduler()
    
    if mode == "start":
        console.print("[bold blue]Starting automated scheduler...[/bold blue]")
        if daemon:
            scheduler_manager.start_daemon()
        else:
            scheduler_manager.start()
        console.print("[bold green]✓ Scheduler started![/bold green]")
    
    elif mode == "stop":
        console.print("[bold blue]Stopping scheduler...[/bold blue]")
        scheduler_manager.stop()
        console.print("[bold green]✓ Scheduler stopped![/bold green]")
    
    elif mode == "status":
        status = scheduler_manager.get_status()
        console.print(f"[bold blue]Scheduler Status:[/bold blue] {status}")

@app.command()
def server(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the server on"),
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind the server to")
):
    """Start the API server."""
    console.print(f"[bold blue]Starting API server on {host}:{port}...[/bold blue]")
    
    import uvicorn
    app_instance = create_app()
    uvicorn.run(app_instance, host=host, port=port)

@app.command()
def status():
    """Show system status."""
    from core.system_monitor import SystemMonitor
    
    monitor = SystemMonitor()
    status_info = monitor.get_system_status()
    
    table = Table(title="System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")
    
    for component, info in status_info.items():
        table.add_row(component, info.get("status", "Unknown"), info.get("details", ""))
    
    console.print(table)

@app.command()
def train(
    incremental: bool = typer.Option(True, "--incremental", "-i", help="Incremental training"),
    force: bool = typer.Option(False, "--force", "-f", help="Force full retraining")
):
    """Trigger model training/updating."""
    console.print("[bold blue]Starting training process...[/bold blue]")
    
    from models.training_manager import TrainingManager
    
    async def run_training():
        trainer = TrainingManager()
        await trainer.train_models(incremental=incremental and not force)
    
    asyncio.run(run_training())
    console.print("[bold green]✓ Training completed![/bold green]")

if __name__ == "__main__":
    app()
