"""
FastAPI server for the semiconductor learning system
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from fastapi import FastAPI, HTTPException, Query, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    FastAPI = None
    HTTPException = None
    Query = None
    Depends = None
    CORSMiddleware = None
    JSONResponse = None
    BaseModel = None
    uvicorn = None

from core.config import config
from core.database import db_manager
from core.system_monitor import system_monitor
from rag.query_engine import query_engine
from crawlers.crawler_manager import crawler_manager

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
if BaseModel:
    class QueryRequest(BaseModel):
        question: str
        include_sources: bool = True
        max_sources: int = 10
        collections: Optional[List[str]] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[Dict[str, Any]]
        confidence: float
        processing_time: float
        timestamp: str

    class CrawlRequest(BaseModel):
        source_filter: Optional[str] = None
        update_existing: bool = False

    class SystemStatus(BaseModel):
        timestamp: str
        overall_status: str
        components: Dict[str, Any]

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    if FastAPI is None:
        raise ImportError("FastAPI not available")
    
    app = FastAPI(
        title="Semiconductor Manufacturing Learning System",
        description="AI-powered system for learning about semiconductor manufacturing and technology",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize the system on startup"""
        try:
            await db_manager.initialize()
            logger.info("API server started and database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize system on startup: {e}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up on shutdown"""
        try:
            await db_manager.close()
            await crawler_manager.close()
            logger.info("API server shut down successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    @app.get("/")
    async def root():
        """Root endpoint with system information"""
        return {
            "message": "Semiconductor Manufacturing Learning System API",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "docs": "/docs",
            "health": "/health"
        }
    
    @app.get("/health", response_model=Dict[str, Any])
    async def health_check():
        """Health check endpoint"""
        try:
            status = system_monitor.get_system_status()
            
            # Log health check
            system_monitor.log_health_check(status)
            
            # Return appropriate HTTP status code
            if status["overall_status"] in ["error", "unhealthy"]:
                return JSONResponse(status_code=503, content=status)
            elif status["overall_status"] == "warning":
                return JSONResponse(status_code=200, content=status)
            else:
                return status
                
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Health check failed", "details": str(e)}
            )
    
    @app.post("/query", response_model=QueryResponse)
    async def query_knowledge_base(request: QueryRequest):
        """Query the semiconductor knowledge base"""
        try:
            response = await query_engine.query(
                question=request.question,
                include_sources=request.include_sources,
                max_sources=request.max_sources,
                collections=request.collections
            )
            
            return QueryResponse(
                answer=response.answer,
                sources=response.sources,
                confidence=response.confidence,
                processing_time=response.processing_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
    
    @app.get("/query")
    async def query_get(
        q: str = Query(..., description="Question to ask"),
        include_sources: bool = Query(True, description="Include source documents"),
        max_sources: int = Query(10, description="Maximum number of sources")
    ):
        """GET endpoint for simple queries"""
        try:
            response = await query_engine.query(
                question=q,
                include_sources=include_sources,
                max_sources=max_sources
            )
            
            return {
                "answer": response.answer,
                "sources": response.sources if include_sources else [],
                "confidence": response.confidence,
                "processing_time": response.processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing GET query: {e}")
            raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
    
    @app.post("/crawl")
    async def trigger_crawl(request: CrawlRequest):
        """Trigger manual crawling"""
        try:
            await crawler_manager.crawl_sources(
                source_filter=request.source_filter,
                update_existing=request.update_existing
            )
            
            return {
                "message": "Crawling completed successfully",
                "timestamp": datetime.now().isoformat(),
                "source_filter": request.source_filter,
                "update_existing": request.update_existing
            }
            
        except Exception as e:
            logger.error(f"Error in manual crawl: {e}")
            raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")
    
    @app.get("/crawl/status")
    async def get_crawl_status():
        """Get crawling status and statistics"""
        try:
            stats = await crawler_manager.get_crawl_statistics()
            return {
                "status": "success",
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting crawl status: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get crawl status: {str(e)}")
    
    @app.get("/data/stats")
    async def get_data_statistics():
        """Get data statistics from the database"""
        try:
            stats = await db_manager.get_system_stats()
            return {
                "status": "success",
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting data stats: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get data statistics: {str(e)}")
    
    @app.get("/historical-timeline")
    async def get_historical_timeline(
        topic: str = Query("semiconductor manufacturing", description="Topic for timeline"),
        limit: int = Query(50, description="Maximum number of events")
    ):
        """Get historical timeline for a semiconductor topic"""
        try:
            timeline = await query_engine.get_historical_timeline(topic)
            
            # Limit results if requested
            if limit and timeline.get("timeline"):
                timeline["timeline"] = timeline["timeline"][:limit]
                timeline["limited_to"] = limit
            
            return {
                "status": "success",
                "timeline": timeline,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting timeline: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get timeline: {str(e)}")
    
    @app.post("/training/trigger")
    async def trigger_training(incremental: bool = Query(True, description="Incremental training")):
        """Trigger model training"""
        try:
            from models.training_manager import training_manager
            
            result = await training_manager.train_models(incremental=incremental)
            
            return {
                "status": "success",
                "training_result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error triggering training: {e}")
            raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
    
    @app.get("/training/history")
    async def get_training_history():
        """Get training history"""
        try:
            from models.training_manager import training_manager
            
            history = await training_manager.get_training_history()
            
            return {
                "status": "success",
                "history": history,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting training history: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get training history: {str(e)}")
    
    @app.get("/models/info")
    async def get_model_info():
        """Get information about current models"""
        try:
            from models.training_manager import training_manager
            
            info = await training_manager.get_model_info()
            
            return {
                "status": "success",
                "model_info": info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")
    
    @app.get("/performance")
    async def get_performance_metrics():
        """Get system performance metrics"""
        try:
            metrics = system_monitor.get_performance_metrics()
            
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")
    
    return app

# Global app instance
app = create_app() if FastAPI else None

if __name__ == "__main__":
    if uvicorn and app:
        uvicorn.run(
            app,
            host=config.api_host,
            port=config.api_port,
            reload=config.debug_mode
        )
    else:
        print("FastAPI or uvicorn not available")
