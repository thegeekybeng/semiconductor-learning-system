"""
Semiconductor Manufacturing Self-Learning Module
Simplified main entry point
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Semiconductor Manufacturing Self-Learning System")
        print("Usage: python main.py <command>")
        print("Commands:")
        print("  init     - Initialize the system")
        print("  status   - Show system status")
        print("  crawl    - Start crawling")
        print("  query    - Query the system")
        print("  demo     - Launch Streamlit demo")
        print("  server   - Start API server")
        return
    
    command = sys.argv[1]
    
    if command == "init":
        print("Initializing system...")
        try:
            from scripts.init_system import initialize_system
            success = asyncio.run(initialize_system(force="--force" in sys.argv))
            if success:
                print("✓ System initialized successfully!")
            else:
                print("✗ System initialization failed!")
                sys.exit(1)
        except Exception as e:
            print(f"Error during initialization: {e}")
            sys.exit(1)
    
    elif command == "status":
        print("Checking system status...")
        try:
            from core.system_monitor import system_monitor
            status = system_monitor.get_system_status()
            print(f"Overall status: {status.get('overall_status', 'unknown')}")
            for component, details in status.items():
                if isinstance(details, dict) and 'status' in details:
                    print(f"  {component}: {details['status']}")
        except Exception as e:
            print(f"Error checking status: {e}")
    
    elif command == "crawl":
        print("Starting crawl...")
        try:
            async def run_crawl():
                from crawlers.crawler_manager import crawler_manager
                await crawler_manager.crawl_sources()
            
            asyncio.run(run_crawl())
            print("✓ Crawling completed!")
        except Exception as e:
            print(f"Error during crawling: {e}")
    
    elif command == "query" and len(sys.argv) > 2:
        question = " ".join(sys.argv[2:])
        print(f"Querying: {question}")
        try:
            from rag.query_engine import query_engine
            response = query_engine.query(question)
            print(f"Answer: {response.answer}")
        except Exception as e:
            print(f"Error during query: {e}")
    
    elif command == "demo":
        print("Starting Streamlit demo...")
        try:
            import subprocess
            subprocess.run(["streamlit", "run", "streamlit_demo.py", "--server.port", "8501"])
        except Exception as e:
            print(f"Error starting demo: {e}")
            print("Please run: streamlit run streamlit_demo.py")
    
    elif command == "server":
        print("Starting API server...")
        try:
            from api.server import app, uvicorn
            if app and uvicorn:
                uvicorn.run(app, host="0.0.0.0", port=8000)
            else:
                print("FastAPI not available")
        except Exception as e:
            print(f"Error starting server: {e}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
