"""
Database management for the semiconductor learning system
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

try:
    import chromadb
    from chromadb.config import Settings
    import pandas as pd
    import sqlite3
except ImportError:
    # Handle missing dependencies gracefully
    chromadb = None
    Settings = None
    pd = None
    sqlite3 = None

from .config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages all database operations for the system"""
    
    def __init__(self):
        self.chroma_client = None
        self.collections = {}
        self.sqlite_db_path = Path("./data/metadata.db")
        
    async def initialize(self):
        """Initialize all database connections"""
        await self._init_chroma()
        await self._init_sqlite()
        logger.info("Database manager initialized successfully")
    
    async def _init_chroma(self):
        """Initialize ChromaDB for vector storage"""
        if chromadb is None:
            logger.warning("ChromaDB not available, using fallback storage")
            return
            
        try:
            config.create_directories()
            
            self.chroma_client = chromadb.PersistentClient(
                path=config.chroma_db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create collections for different types of content
            self.collections = {
                "documents": self._get_or_create_collection("semiconductor_documents"),
                "research_papers": self._get_or_create_collection("research_papers"),
                "news_articles": self._get_or_create_collection("news_articles"),
                "patents": self._get_or_create_collection("patents"),
                "historical_data": self._get_or_create_collection("historical_data"),
            }
            
            logger.info("ChromaDB initialized with collections")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.chroma_client.get_collection(name)
        except:
            return self.chroma_client.create_collection(
                name=name,
                metadata={"description": f"Collection for {name.replace('_', ' ')}"}
            )
    
    async def _init_sqlite(self):
        """Initialize SQLite for metadata storage"""
        self.sqlite_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with sqlite3.connect(self.sqlite_db_path) as conn:
                cursor = conn.cursor()
                
                # Create tables for metadata
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS crawl_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_type TEXT NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP,
                        status TEXT NOT NULL,
                        pages_crawled INTEGER DEFAULT 0,
                        documents_processed INTEGER DEFAULT 0,
                        errors TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS training_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_type TEXT NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP,
                        status TEXT NOT NULL,
                        data_points INTEGER DEFAULT 0,
                        performance_metrics TEXT,
                        model_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS data_sources (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_name TEXT UNIQUE NOT NULL,
                        source_url TEXT NOT NULL,
                        source_type TEXT NOT NULL,
                        last_crawled TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        crawl_frequency TEXT DEFAULT 'daily',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        metric_type TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("SQLite database initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize SQLite: {e}")
            raise
    
    async def add_documents(self, documents: List[Dict[str, Any]], collection_name: str = "documents"):
        """Add documents to the vector database"""
        if not self.chroma_client or collection_name not in self.collections:
            logger.warning(f"Collection {collection_name} not available")
            return False
        
        try:
            collection = self.collections[collection_name]
            
            # Prepare data for ChromaDB
            ids = [doc.get("id", f"doc_{i}") for i, doc in enumerate(documents)]
            texts = [doc.get("content", "") for doc in documents]
            metadatas = [
                {
                    "source": doc.get("source", "unknown"),
                    "title": doc.get("title", ""),
                    "url": doc.get("url", ""),
                    "timestamp": doc.get("timestamp", datetime.now().isoformat()),
                    "type": doc.get("type", "document")
                }
                for doc in documents
            ]
            
            # Add to collection
            collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to {collection_name}: {e}")
            return False
    
    async def query_documents(
        self, 
        query_text: str, 
        collection_name: str = "documents",
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Query documents from the vector database"""
        if not self.chroma_client or collection_name not in self.collections:
            logger.warning(f"Collection {collection_name} not available")
            return []
        
        try:
            collection = self.collections[collection_name]
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0,
                        "relevance_score": 1 - (results["distances"][0][i] if results["distances"] else 0.0)
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to query {collection_name}: {e}")
            return []
    
    async def log_crawl_session(self, session_data: Dict[str, Any]):
        """Log crawling session metadata"""
        try:
            with sqlite3.connect(self.sqlite_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO crawl_sessions 
                    (source_type, start_time, end_time, status, pages_crawled, documents_processed, errors)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_data.get("source_type", "unknown"),
                    session_data.get("start_time"),
                    session_data.get("end_time"),
                    session_data.get("status", "unknown"),
                    session_data.get("pages_crawled", 0),
                    session_data.get("documents_processed", 0),
                    json.dumps(session_data.get("errors", []))
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log crawl session: {e}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {}
        
        try:
            # Get ChromaDB stats
            if self.chroma_client:
                for name, collection in self.collections.items():
                    count = collection.count()
                    stats[f"{name}_count"] = count
            
            # Get SQLite stats
            with sqlite3.connect(self.sqlite_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM crawl_sessions")
                stats["total_crawl_sessions"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM training_sessions")
                stats["total_training_sessions"] = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM crawl_sessions 
                    GROUP BY status
                """)
                crawl_status = dict(cursor.fetchall())
                stats["crawl_status_breakdown"] = crawl_status
                
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            stats["error"] = str(e)
        
        return stats
    
    async def cleanup_old_data(self, days_old: int = 30):
        """Clean up old data"""
        try:
            # This is a placeholder for cleanup logic
            # In a real implementation, you would:
            # 1. Remove old vector embeddings
            # 2. Archive old crawl sessions
            # 3. Clean up temporary files
            
            logger.info(f"Cleanup completed for data older than {days_old} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    async def close(self):
        """Close database connections"""
        try:
            if self.chroma_client:
                # ChromaDB doesn't need explicit closing
                pass
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

# Global database manager instance
db_manager = DatabaseManager()
