"""
Core configuration management for the semiconductor learning system
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

# Handle missing dependencies gracefully
try:
    from pydantic import BaseSettings, Field
except ImportError:
    # Fallback implementation without Pydantic
    BaseSettings = object
    def Field(default=None, env=None):
        return default

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    def load_dotenv():
        pass
    load_dotenv()

class Config(BaseSettings if BaseSettings != object else object):
    """Main configuration class using Pydantic BaseSettings"""
    
    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.1, env="OPENAI_TEMPERATURE")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    
    # Database Configuration
    chroma_db_path: str = Field(default="./data/chroma_db", env="CHROMA_DB_PATH")
    postgres_url: str = Field(default="", env="POSTGRES_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Crawling Configuration
    max_crawl_depth: int = Field(default=3, env="MAX_CRAWL_DEPTH")
    crawl_delay: int = Field(default=2, env="CRAWL_DELAY")
    max_pages_per_source: int = Field(default=100, env="MAX_PAGES_PER_SOURCE")
    user_agent: str = Field(default="SemiconductorLearningBot/1.0", env="USER_AGENT")
    
    # Scheduling Configuration
    crawl_schedule: str = Field(default="0 2 * * *", env="CRAWL_SCHEDULE")
    training_schedule: str = Field(default="0 4 * * 0", env="TRAINING_SCHEDULE")
    cleanup_schedule: str = Field(default="0 1 * * 0", env="CLEANUP_SCHEDULE")
    
    # RAG Configuration
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    top_k_results: int = Field(default=10, env="TOP_K_RESULTS")
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    
    # Model Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", 
        env="EMBEDDING_MODEL"
    )
    rerank_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2", 
        env="RERANK_MODEL"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/semiconductor_learning.log", env="LOG_FILE")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    
    # Data Sources Configuration
    enable_arxiv_crawling: bool = Field(default=True, env="ENABLE_ARXIV_CRAWLING")
    enable_ieee_crawling: bool = Field(default=True, env="ENABLE_IEEE_CRAWLING")
    enable_semiconductor_news: bool = Field(default=True, env="ENABLE_SEMICONDUCTOR_NEWS")
    enable_patent_crawling: bool = Field(default=True, env="ENABLE_PATENT_CRAWLING")
    enable_industry_reports: bool = Field(default=True, env="ENABLE_INDUSTRY_REPORTS")
    
    # Performance Configuration
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    batch_size: int = Field(default=32, env="BATCH_SIZE")
    vector_dimension: int = Field(default=384, env="VECTOR_DIMENSION")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_data_sources(self) -> Dict[str, bool]:
        """Get enabled data sources"""
        return {
            "arxiv": self.enable_arxiv_crawling,
            "ieee": self.enable_ieee_crawling,
            "semiconductor_news": self.enable_semiconductor_news,
            "patents": self.enable_patent_crawling,
            "industry_reports": self.enable_industry_reports,
        }
    
    def get_schedules(self) -> Dict[str, str]:
        """Get all configured schedules"""
        return {
            "crawl": self.crawl_schedule,
            "training": self.training_schedule,
            "cleanup": self.cleanup_schedule,
        }
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            Path(self.chroma_db_path).parent,
            Path(self.log_file).parent,
            Path("./data"),
            Path("./logs"),
            Path("./models"),
            Path("./cache"),
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

# Global configuration instance
config = Config()
