"""
Main scheduler for automated learning and data updates
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading
import time

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    import schedule
except ImportError:
    AsyncIOScheduler = None
    CronTrigger = None
    IntervalTrigger = None
    schedule = None

from core.config import config
from core.database import db_manager
from crawlers.crawler_manager import crawler_manager

logger = logging.getLogger(__name__)

class MainScheduler:
    """Main scheduler that coordinates all automated tasks"""
    
    def __init__(self):
        self.scheduler = None
        self.is_running = False
        self.background_thread = None
        self._shutdown_event = threading.Event()
        
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            if AsyncIOScheduler:
                self._start_advanced_scheduler()
            else:
                self._start_basic_scheduler()
                
            self.is_running = True
            logger.info("Main scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def _start_advanced_scheduler(self):
        """Start the advanced APScheduler-based scheduler"""
        self.scheduler = AsyncIOScheduler()
        
        # Add jobs based on configuration
        self._add_scheduled_jobs()
        
        # Start the scheduler
        self.scheduler.start()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _start_basic_scheduler(self):
        """Start the basic schedule-based scheduler as fallback"""
        if schedule is None:
            logger.error("No scheduling library available")
            return
        
        # Parse cron-like schedules into schedule library format
        self._schedule_basic_jobs()
        
        # Start scheduler in background thread
        self.background_thread = threading.Thread(target=self._run_basic_scheduler)
        self.background_thread.daemon = True
        self.background_thread.start()
    
    def _add_scheduled_jobs(self):
        """Add all scheduled jobs to the advanced scheduler"""
        
        # Daily crawling job
        try:
            crawl_trigger = CronTrigger.from_crontab(config.crawl_schedule)
            self.scheduler.add_job(
                self._run_crawling_job,
                trigger=crawl_trigger,
                id="daily_crawl",
                name="Daily Data Crawling",
                max_instances=1,
                coalesce=True
            )
            logger.info(f"Scheduled daily crawling: {config.crawl_schedule}")
        except Exception as e:
            logger.error(f"Failed to schedule crawling job: {e}")
        
        # Weekly training job
        try:
            training_trigger = CronTrigger.from_crontab(config.training_schedule)
            self.scheduler.add_job(
                self._run_training_job,
                trigger=training_trigger,
                id="weekly_training",
                name="Weekly Model Training",
                max_instances=1,
                coalesce=True
            )
            logger.info(f"Scheduled weekly training: {config.training_schedule}")
        except Exception as e:
            logger.error(f"Failed to schedule training job: {e}")
        
        # Weekly cleanup job
        try:
            cleanup_trigger = CronTrigger.from_crontab(config.cleanup_schedule)
            self.scheduler.add_job(
                self._run_cleanup_job,
                trigger=cleanup_trigger,
                id="weekly_cleanup",
                name="Weekly Data Cleanup",
                max_instances=1,
                coalesce=True
            )
            logger.info(f"Scheduled weekly cleanup: {config.cleanup_schedule}")
        except Exception as e:
            logger.error(f"Failed to schedule cleanup job: {e}")
        
        # Health check job (every hour)
        self.scheduler.add_job(
            self._run_health_check,
            trigger=IntervalTrigger(hours=1),
            id="health_check",
            name="System Health Check",
            max_instances=1
        )
        logger.info("Scheduled hourly health checks")
    
    def _schedule_basic_jobs(self):
        """Schedule jobs using the basic schedule library"""
        
        # Parse cron schedules to schedule library format
        # This is a simplified implementation
        
        # Daily crawling (assuming 2 AM daily from default config)
        schedule.every().day.at("02:00").do(self._async_job_wrapper, self._run_crawling_job)
        
        # Weekly training (assuming Sunday 4 AM from default config)
        schedule.every().sunday.at("04:00").do(self._async_job_wrapper, self._run_training_job)
        
        # Weekly cleanup (assuming Sunday 1 AM from default config)
        schedule.every().sunday.at("01:00").do(self._async_job_wrapper, self._run_cleanup_job)
        
        # Health check every hour
        schedule.every().hour.do(self._async_job_wrapper, self._run_health_check)
        
        logger.info("Basic scheduler jobs configured")
    
    def _run_basic_scheduler(self):
        """Run the basic scheduler in a background thread"""
        while not self._shutdown_event.is_set():
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _async_job_wrapper(self, async_func):
        """Wrapper to run async functions in the basic scheduler"""
        def wrapper():
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(async_func())
                loop.close()
            except Exception as e:
                logger.error(f"Error in scheduled job: {e}")
        
        return wrapper()
    
    async def _run_crawling_job(self):
        """Execute the crawling job"""
        logger.info("Starting scheduled crawling job")
        
        try:
            # Initialize database if needed
            if not hasattr(db_manager, 'chroma_client') or db_manager.chroma_client is None:
                await db_manager.initialize()
            
            # Run crawling
            await crawler_manager.crawl_sources(update_existing=False)
            
            logger.info("Scheduled crawling job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in crawling job: {e}")
    
    async def _run_training_job(self):
        """Execute the training job"""
        logger.info("Starting scheduled training job")
        
        try:
            # Import here to avoid circular imports
            from models.training_manager import TrainingManager
            
            trainer = TrainingManager()
            await trainer.train_models(incremental=True)
            
            logger.info("Scheduled training job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in training job: {e}")
    
    async def _run_cleanup_job(self):
        """Execute the cleanup job"""
        logger.info("Starting scheduled cleanup job")
        
        try:
            # Clean up old data
            await db_manager.cleanup_old_data(days_old=30)
            
            # Additional cleanup tasks can be added here
            
            logger.info("Scheduled cleanup job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in cleanup job: {e}")
    
    async def _run_health_check(self):
        """Execute health check"""
        try:
            # Check system health
            from core.system_monitor import SystemMonitor
            
            monitor = SystemMonitor()
            health_status = monitor.get_system_status()
            
            # Log any issues
            for component, status in health_status.items():
                if status.get("status") != "healthy":
                    logger.warning(f"Health check - {component}: {status}")
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            if self.scheduler:
                self.scheduler.shutdown(wait=False)
            
            if self.background_thread:
                self._shutdown_event.set()
                self.background_thread.join(timeout=10)
            
            self.is_running = False
            logger.info("Scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        status = {
            "is_running": self.is_running,
            "scheduler_type": "advanced" if AsyncIOScheduler else "basic",
            "jobs": []
        }
        
        if self.scheduler and hasattr(self.scheduler, 'get_jobs'):
            try:
                jobs = self.scheduler.get_jobs()
                status["jobs"] = [
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                        "trigger": str(job.trigger)
                    }
                    for job in jobs
                ]
            except Exception as e:
                logger.error(f"Error getting job status: {e}")
        
        return status
    
    def start_daemon(self):
        """Start scheduler as a daemon process"""
        self.start()
        
        try:
            if self.scheduler:
                # Keep the main thread alive
                while self.is_running:
                    asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))
            else:
                # For basic scheduler, just wait
                while self.is_running:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            self.stop()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down scheduler")
        self.stop()
        sys.exit(0)

# Global scheduler instance
main_scheduler = MainScheduler()
