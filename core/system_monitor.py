"""
System monitoring and health checks
"""

import logging
import psutil
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from core.config import config
from core.database import db_manager

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitors system health and performance"""
    
    def __init__(self):
        self.last_check_time = None
        self.health_history = []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy"
        }
        
        try:
            # Check system resources
            status["system_resources"] = self._check_system_resources()
            
            # Check database health
            status["database"] = self._check_database_health()
            
            # Check file system
            status["filesystem"] = self._check_filesystem_health()
            
            # Check configuration
            status["configuration"] = self._check_configuration()
            
            # Check data freshness
            status["data_freshness"] = self._check_data_freshness()
            
            # Determine overall status
            status["overall_status"] = self._determine_overall_status(status)
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            status["error"] = str(e)
            status["overall_status"] = "error"
        
        self.last_check_time = datetime.now()
        return status
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy" if cpu_percent < 80 and memory.percent < 80 and disk.percent < 90 else "warning",
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return {"status": "error", "details": str(e)}
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        
        try:
            # Check if database is initialized
            if not hasattr(db_manager, 'chroma_client') or db_manager.chroma_client is None:
                return {
                    "status": "unhealthy",
                    "details": "Database not initialized"
                }
            
            # Check database file existence
            db_path = Path(config.chroma_db_path)
            if not db_path.exists():
                return {
                    "status": "warning",
                    "details": "Database path does not exist"
                }
            
            # Check collections
            collection_status = {}
            try:
                for collection_name in ["documents", "research_papers", "news_articles", "patents", "historical_data"]:
                    if collection_name in db_manager.collections:
                        collection = db_manager.collections[collection_name]
                        count = collection.count()
                        collection_status[collection_name] = {"count": count, "status": "healthy"}
                    else:
                        collection_status[collection_name] = {"status": "missing"}
            except Exception as e:
                collection_status["error"] = str(e)
            
            return {
                "status": "healthy",
                "details": {
                    "database_path": str(db_path),
                    "collections": collection_status
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking database health: {e}")
            return {"status": "error", "details": str(e)}
    
    def _check_filesystem_health(self) -> Dict[str, Any]:
        """Check filesystem health and required directories"""
        
        try:
            required_dirs = [
                Path(config.chroma_db_path).parent,
                Path(config.log_file).parent,
                Path("./data"),
                Path("./logs"),
                Path("./models"),
                Path("./cache")
            ]
            
            dir_status = {}
            all_healthy = True
            
            for dir_path in required_dirs:
                if dir_path.exists() and dir_path.is_dir():
                    # Check write permissions
                    try:
                        test_file = dir_path / ".test_write"
                        test_file.touch()
                        test_file.unlink()
                        dir_status[str(dir_path)] = {"status": "healthy", "writable": True}
                    except Exception:
                        dir_status[str(dir_path)] = {"status": "warning", "writable": False}
                        all_healthy = False
                else:
                    dir_status[str(dir_path)] = {"status": "missing", "writable": False}
                    all_healthy = False
            
            return {
                "status": "healthy" if all_healthy else "warning",
                "details": dir_status
            }
            
        except Exception as e:
            logger.error(f"Error checking filesystem health: {e}")
            return {"status": "error", "details": str(e)}
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration validity"""
        
        try:
            config_issues = []
            
            # Check required API keys
            if not config.openai_api_key:
                config_issues.append("OpenAI API key not configured")
            
            # Check paths
            if not config.chroma_db_path:
                config_issues.append("ChromaDB path not configured")
            
            # Check data source configurations
            data_sources = config.get_data_sources()
            enabled_sources = [name for name, enabled in data_sources.items() if enabled]
            
            if not enabled_sources:
                config_issues.append("No data sources enabled")
            
            return {
                "status": "healthy" if not config_issues else "warning",
                "details": {
                    "issues": config_issues,
                    "enabled_data_sources": enabled_sources,
                    "api_keys_configured": {
                        "openai": bool(config.openai_api_key),
                        "anthropic": bool(config.anthropic_api_key)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking configuration: {e}")
            return {"status": "error", "details": str(e)}
    
    def _check_data_freshness(self) -> Dict[str, Any]:
        """Check how fresh the data is"""
        
        try:
            # This would check the last crawl times and data update times
            # For now, it's a placeholder
            
            return {
                "status": "healthy",
                "details": {
                    "last_crawl": "Unknown",  # Would be populated from database
                    "last_training": "Unknown",  # Would be populated from database
                    "data_age_days": "Unknown"
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking data freshness: {e}")
            return {"status": "error", "details": str(e)}
    
    def _determine_overall_status(self, status_dict: Dict[str, Any]) -> str:
        """Determine overall system status based on component statuses"""
        
        component_statuses = []
        
        for key, value in status_dict.items():
            if isinstance(value, dict) and "status" in value:
                component_statuses.append(value["status"])
        
        if "error" in component_statuses:
            return "error"
        elif "unhealthy" in component_statuses:
            return "unhealthy"
        elif "warning" in component_statuses:
            return "warning"
        else:
            return "healthy"
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "process_count": len(psutil.pids()),
                "uptime_seconds": self._get_system_uptime()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    def _get_system_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
            return uptime_seconds
        except:
            # Fallback for non-Linux systems
            return 0.0
    
    def log_health_check(self, status: Dict[str, Any]):
        """Log health check results"""
        
        try:
            # Add to history
            self.health_history.append({
                "timestamp": datetime.now().isoformat(),
                "status": status
            })
            
            # Keep only recent history (last 100 checks)
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
            # Log warnings and errors
            overall_status = status.get("overall_status", "unknown")
            if overall_status in ["warning", "error", "unhealthy"]:
                logger.warning(f"System health check: {overall_status}")
                
                # Log specific issues
                for component, details in status.items():
                    if isinstance(details, dict) and details.get("status") in ["warning", "error", "unhealthy"]:
                        logger.warning(f"{component}: {details}")
            
        except Exception as e:
            logger.error(f"Error logging health check: {e}")

# Global system monitor instance
system_monitor = SystemMonitor()
