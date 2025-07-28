"""
System initialization script
"""

import asyncio
import logging
import sys
from pathlib import Path

from core.config import config
from core.database import db_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.log_file) if Path(config.log_file).parent.exists() else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate that all required environment variables and dependencies are set"""
    issues = []
    
    # Check required configurations
    if not config.openai_api_key:
        issues.append("OPENAI_API_KEY is not set")
    
    # Check required directories can be created
    try:
        config.create_directories()
    except Exception as e:
        issues.append(f"Cannot create required directories: {e}")
    
    # Check if we can write to log directory
    log_dir = Path(config.log_file).parent
    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create log directory: {e}")
    
    return issues

async def initialize_database():
    """Initialize the database system"""
    logger.info("Initializing database...")
    
    try:
        await db_manager.initialize()
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def setup_data_sources():
    """Set up initial data sources configuration"""
    logger.info("Setting up data sources...")
    
    try:
        # This would typically involve:
        # 1. Creating initial data source entries in the database
        # 2. Validating data source URLs
        # 3. Setting up initial crawling schedules
        
        # For now, we'll just validate that sources are configured
        data_sources = config.get_data_sources()
        enabled_sources = [name for name, enabled in data_sources.items() if enabled]
        
        if not enabled_sources:
            logger.warning("No data sources are enabled")
            return False
        
        logger.info(f"Configured data sources: {', '.join(enabled_sources)}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set up data sources: {e}")
        return False

def create_initial_directories():
    """Create all required directories"""
    logger.info("Creating required directories...")
    
    try:
        config.create_directories()
        
        # Additional directories for specific components
        additional_dirs = [
            "./cache/crawl",
            "./cache/models",
            "./data/exports",
            "./data/imports",
            "./logs/crawl",
            "./logs/training"
        ]
        
        for dir_path in additional_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        logger.info("All directories created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        return False

async def run_initial_health_check():
    """Run an initial health check"""
    logger.info("Running initial health check...")
    
    try:
        from core.system_monitor import system_monitor
        
        status = system_monitor.get_system_status()
        
        if status["overall_status"] == "healthy":
            logger.info("Initial health check passed")
            return True
        else:
            logger.warning(f"Health check status: {status['overall_status']}")
            
            # Log specific issues
            for component, details in status.items():
                if isinstance(details, dict) and details.get("status") != "healthy":
                    logger.warning(f"{component}: {details}")
            
            return False
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

async def initialize_system(force: bool = False) -> bool:
    """
    Initialize the entire system
    
    Args:
        force: Force re-initialization even if already initialized
    
    Returns:
        True if initialization successful, False otherwise
    """
    logger.info("Starting system initialization...")
    
    # Step 1: Validate environment
    logger.info("Step 1: Validating environment...")
    env_issues = validate_environment()
    if env_issues:
        logger.error("Environment validation failed:")
        for issue in env_issues:
            logger.error(f"  - {issue}")
        
        if not force:
            logger.error("Use --force flag to proceed anyway")
            return False
        else:
            logger.warning("Proceeding with environment issues due to --force flag")
    
    # Step 2: Create directories
    logger.info("Step 2: Creating directories...")
    if not create_initial_directories():
        logger.error("Failed to create required directories")
        return False
    
    # Step 3: Initialize database
    logger.info("Step 3: Initializing database...")
    if not await initialize_database():
        logger.error("Failed to initialize database")
        return False
    
    # Step 4: Set up data sources
    logger.info("Step 4: Setting up data sources...")
    if not setup_data_sources():
        logger.warning("Data source setup had issues, but continuing...")
    
    # Step 5: Run health check
    logger.info("Step 5: Running initial health check...")
    if not await run_initial_health_check():
        logger.warning("Initial health check had issues, but system is initialized")
    
    logger.info("System initialization completed successfully!")
    
    # Print next steps
    print("\n" + "="*60)
    print("🎉 Semiconductor Learning System Initialized Successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start crawling data:")
    print("   python main.py crawl")
    print("\n2. Query the knowledge base:")
    print("   python main.py query \"How has EUV lithography evolved?\"")
    print("\n3. Start the API server:")
    print("   python main.py server")
    print("\n4. Start automated scheduling:")
    print("   python main.py scheduler")
    print("\n5. Check system status:")
    print("   python main.py status")
    print("\n" + "="*60)
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize the Semiconductor Learning System")
    parser.add_argument("--force", action="store_true", help="Force initialization even with issues")
    
    args = parser.parse_args()
    
    success = asyncio.run(initialize_system(force=args.force))
    sys.exit(0 if success else 1)
