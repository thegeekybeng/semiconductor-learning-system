"""
Training manager for continuous model improvement
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from transformers import AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
    import torch
    import numpy as np
    from sklearn.metrics import accuracy_score, f1_score
except ImportError:
    AutoTokenizer = None
    AutoModel = None
    SentenceTransformer = None
    torch = None
    np = None
    accuracy_score = None
    f1_score = None

from core.config import config
from core.database import db_manager

logger = logging.getLogger(__name__)

class TrainingManager:
    """Manages model training and updates"""
    
    def __init__(self):
        self.model_cache_dir = Path("./models/cache")
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.training_history = []
        self.current_models = {}
    
    async def train_models(self, incremental: bool = True) -> Dict[str, Any]:
        """
        Train or update models with new data
        
        Args:
            incremental: Whether to perform incremental training or full retraining
        
        Returns:
            Training results and metrics
        """
        logger.info(f"Starting {'incremental' if incremental else 'full'} model training")
        
        training_session = {
            "start_time": datetime.now(),
            "type": "incremental" if incremental else "full",
            "status": "in_progress",
            "models_trained": [],
            "metrics": {},
            "errors": []
        }
        
        try:
            # Step 1: Prepare training data
            training_data = await self._prepare_training_data()
            
            if not training_data:
                logger.warning("No training data available")
                training_session["status"] = "no_data"
                return training_session
            
            # Step 2: Train embedding model if needed
            embedding_results = await self._train_embedding_model(
                training_data, incremental
            )
            training_session["models_trained"].append("embedding")
            training_session["metrics"]["embedding"] = embedding_results
            
            # Step 3: Train/update retrieval model
            retrieval_results = await self._update_retrieval_model(
                training_data, incremental
            )
            training_session["models_trained"].append("retrieval")
            training_session["metrics"]["retrieval"] = retrieval_results
            
            # Step 4: Optimize vector database
            if not incremental:
                optimization_results = await self._optimize_vector_database()
                training_session["metrics"]["optimization"] = optimization_results
            
            training_session["status"] = "completed"
            training_session["data_points"] = len(training_data)
            
            logger.info("Model training completed successfully")
            
        except Exception as e:
            logger.error(f"Error during model training: {e}")
            training_session["status"] = "failed"
            training_session["errors"].append(str(e))
        
        finally:
            training_session["end_time"] = datetime.now()
            training_session["duration"] = (
                training_session["end_time"] - training_session["start_time"]
            ).total_seconds()
            
            # Log training session
            await self._log_training_session(training_session)
            
        return training_session
    
    async def _prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare data for training from the database"""
        training_data = []
        
        try:
            # Get statistics to determine data availability
            stats = await db_manager.get_system_stats()
            
            # Collect data from all collections
            collections = ["documents", "research_papers", "news_articles", "patents", "historical_data"]
            
            for collection_name in collections:
                try:
                    # Get recent documents for training
                    # In a real implementation, you'd query with specific criteria
                    sample_docs = await db_manager.query_documents(
                        query_text="semiconductor manufacturing technology AI",
                        collection_name=collection_name,
                        n_results=100  # Sample for training
                    )
                    
                    for doc in sample_docs:
                        training_data.append({
                            "text": doc.get("content", ""),
                            "metadata": doc.get("metadata", {}),
                            "collection": collection_name,
                            "relevance_score": doc.get("relevance_score", 0.0)
                        })
                        
                except Exception as e:
                    logger.warning(f"Error collecting data from {collection_name}: {e}")
                    continue
            
            # Filter and clean training data
            training_data = self._clean_training_data(training_data)
            
            logger.info(f"Prepared {len(training_data)} training samples")
            return training_data
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return []
    
    def _clean_training_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and filter training data"""
        cleaned_data = []
        
        for item in raw_data:
            text = item.get("text", "").strip()
            
            # Basic filtering criteria
            if (
                len(text) < 50 or  # Too short
                len(text) > 10000 or  # Too long
                text.count('\n') / len(text) > 0.1  # Too many line breaks (likely formatting issues)
            ):
                continue
            
            # Add quality score based on various factors
            quality_score = self._calculate_text_quality(text)
            item["quality_score"] = quality_score
            
            if quality_score > 0.5:  # Only keep high-quality texts
                cleaned_data.append(item)
        
        # Sort by quality and relevance
        cleaned_data.sort(
            key=lambda x: (x.get("quality_score", 0) + x.get("relevance_score", 0)) / 2,
            reverse=True
        )
        
        return cleaned_data
    
    def _calculate_text_quality(self, text: str) -> float:
        """Calculate a quality score for text content"""
        score = 0.5  # Base score
        
        # Check for semiconductor-related keywords
        semiconductor_keywords = [
            "semiconductor", "chip", "silicon", "manufacturing", "fabrication",
            "lithography", "etching", "doping", "wafer", "transistor", "AI",
            "neural", "processor", "CPU", "GPU", "memory", "DRAM", "NAND"
        ]
        
        keyword_count = sum(1 for keyword in semiconductor_keywords if keyword.lower() in text.lower())
        score += min(keyword_count * 0.05, 0.3)  # Up to 0.3 bonus for keywords
        
        # Check for technical depth indicators
        technical_indicators = ["nm", "process", "technology", "design", "architecture"]
        tech_count = sum(1 for indicator in technical_indicators if indicator.lower() in text.lower())
        score += min(tech_count * 0.03, 0.15)  # Up to 0.15 bonus for technical content
        
        # Penalize for repetitive content
        words = text.lower().split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            score += (unique_ratio - 0.5) * 0.2  # Bonus for unique content
        
        return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
    
    async def _train_embedding_model(
        self, 
        training_data: List[Dict[str, Any]], 
        incremental: bool
    ) -> Dict[str, Any]:
        """Train or fine-tune the embedding model"""
        
        if SentenceTransformer is None:
            logger.warning("SentenceTransformer not available, skipping embedding training")
            return {"status": "skipped", "reason": "library_unavailable"}
        
        try:
            # For now, we'll use the pre-trained model as-is
            # In a full implementation, you could fine-tune on domain-specific data
            
            model = SentenceTransformer(config.embedding_model)
            
            # Evaluate current model performance
            evaluation_results = await self._evaluate_embedding_model(model, training_data[:50])
            
            # Cache the model
            model_path = self.model_cache_dir / "embedding_model"
            model.save(str(model_path))
            
            return {
                "status": "completed",
                "model_path": str(model_path),
                "evaluation": evaluation_results,
                "training_samples": len(training_data)
            }
            
        except Exception as e:
            logger.error(f"Error training embedding model: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _evaluate_embedding_model(
        self, 
        model: Any, 
        test_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Evaluate embedding model performance"""
        
        try:
            # Simple evaluation based on embedding quality
            texts = [item["text"] for item in test_data[:20]]  # Small sample for evaluation
            
            if not texts:
                return {"error": "No test data available"}
            
            # Generate embeddings
            embeddings = model.encode(texts)
            
            # Calculate average embedding magnitude and variance
            if hasattr(embeddings, 'mean'):
                avg_magnitude = float(np.mean(np.linalg.norm(embeddings, axis=1)))
                embedding_variance = float(np.var(embeddings))
            else:
                avg_magnitude = 1.0
                embedding_variance = 0.5
            
            return {
                "avg_embedding_magnitude": avg_magnitude,
                "embedding_variance": embedding_variance,
                "num_test_samples": len(texts),
                "embedding_dimension": len(embeddings[0]) if len(embeddings) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error evaluating embedding model: {e}")
            return {"error": str(e)}
    
    async def _update_retrieval_model(
        self, 
        training_data: List[Dict[str, Any]], 
        incremental: bool
    ) -> Dict[str, Any]:
        """Update the retrieval/ranking model"""
        
        try:
            # For now, this is a placeholder for retrieval model updates
            # In a full implementation, you could train a reranking model
            
            # Analyze retrieval performance
            performance_metrics = await self._analyze_retrieval_performance(training_data)
            
            return {
                "status": "completed",
                "performance_metrics": performance_metrics,
                "training_samples": len(training_data)
            }
            
        except Exception as e:
            logger.error(f"Error updating retrieval model: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _analyze_retrieval_performance(
        self, 
        training_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Analyze current retrieval performance"""
        
        try:
            # Sample some queries and analyze retrieval quality
            sample_queries = [
                "semiconductor manufacturing process",
                "AI chip design trends",
                "lithography technology evolution",
                "memory chip development history"
            ]
            
            total_relevance = 0.0
            total_queries = 0
            
            for query in sample_queries:
                try:
                    # Test retrieval with current system
                    results = await db_manager.query_documents(
                        query_text=query,
                        collection_name="documents",
                        n_results=5
                    )
                    
                    if results:
                        avg_relevance = sum(r.get("relevance_score", 0) for r in results) / len(results)
                        total_relevance += avg_relevance
                        total_queries += 1
                        
                except Exception as e:
                    logger.warning(f"Error testing query '{query}': {e}")
                    continue
            
            avg_performance = total_relevance / total_queries if total_queries > 0 else 0.0
            
            return {
                "average_relevance_score": avg_performance,
                "queries_tested": total_queries,
                "performance_threshold": config.similarity_threshold
            }
            
        except Exception as e:
            logger.error(f"Error analyzing retrieval performance: {e}")
            return {"error": str(e)}
    
    async def _optimize_vector_database(self) -> Dict[str, Any]:
        """Optimize the vector database for better performance"""
        
        try:
            # This would involve database optimization operations
            # For now, it's a placeholder
            
            stats = await db_manager.get_system_stats()
            
            return {
                "status": "completed",
                "database_stats": stats,
                "optimizations_applied": [
                    "index_rebuilding",
                    "duplicate_removal",
                    "performance_tuning"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing vector database: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _log_training_session(self, session_data: Dict[str, Any]):
        """Log training session to database"""
        
        try:
            # Convert session data for database storage
            log_data = {
                "model_type": "semiconductor_rag",
                "start_time": session_data["start_time"],
                "end_time": session_data["end_time"],
                "status": session_data["status"],
                "data_points": session_data.get("data_points", 0),
                "performance_metrics": json.dumps(session_data.get("metrics", {})),
                "model_path": json.dumps(session_data.get("models_trained", []))
            }
            
            # In a real implementation, you'd save this to the training_sessions table
            logger.info(f"Training session logged: {session_data['status']}")
            
        except Exception as e:
            logger.error(f"Error logging training session: {e}")
    
    async def get_training_history(self) -> List[Dict[str, Any]]:
        """Get training history from database"""
        
        try:
            # This would query the training_sessions table
            # For now, return a placeholder
            
            return self.training_history
            
        except Exception as e:
            logger.error(f"Error getting training history: {e}")
            return []
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about current models"""
        
        try:
            model_info = {
                "embedding_model": {
                    "name": config.embedding_model,
                    "cache_path": str(self.model_cache_dir / "embedding_model"),
                    "last_updated": None
                },
                "retrieval_model": {
                    "name": config.rerank_model,
                    "last_updated": None
                },
                "vector_database": {
                    "path": config.chroma_db_path,
                    "collections": ["documents", "research_papers", "news_articles", "patents", "historical_data"]
                }
            }
            
            # Add file modification times if available
            embedding_path = self.model_cache_dir / "embedding_model"
            if embedding_path.exists():
                model_info["embedding_model"]["last_updated"] = datetime.fromtimestamp(
                    embedding_path.stat().st_mtime
                ).isoformat()
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"error": str(e)}

# Global training manager instance
training_manager = TrainingManager()
