"""
Crawler management system for semiconductor industry data collection
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    import aiohttp
    import asyncio
except ImportError:
    AsyncWebCrawler = None
    LLMExtractionStrategy = None
    aiohttp = None

from core.config import config
from core.database import db_manager

logger = logging.getLogger(__name__)

class SemiconductorDataSource:
    """Represents a data source for semiconductor information"""
    
    def __init__(self, name: str, urls: List[str], source_type: str, crawl_config: Dict[str, Any] = None):
        self.name = name
        self.urls = urls
        self.source_type = source_type
        self.crawl_config = crawl_config or {}
        self.last_crawled = None
        
    def should_crawl(self, frequency_hours: int = 24) -> bool:
        """Check if this source should be crawled based on frequency"""
        if not self.last_crawled:
            return True
        
        time_since_last = datetime.now() - self.last_crawled
        return time_since_last > timedelta(hours=frequency_hours)

class CrawlerManager:
    """Manages all crawling operations"""
    
    def __init__(self):
        self.data_sources = self._initialize_data_sources()
        self.crawler = None
        
    def _initialize_data_sources(self) -> Dict[str, SemiconductorDataSource]:
        """Initialize all semiconductor data sources"""
        sources = {}
        
        # ArXiv semiconductor research
        if config.enable_arxiv_crawling:
            sources["arxiv"] = SemiconductorDataSource(
                name="ArXiv Semiconductor Research",
                urls=[
                    "https://arxiv.org/search/?query=semiconductor&searchtype=all",
                    "https://arxiv.org/search/?query=silicon+technology&searchtype=all",
                    "https://arxiv.org/search/?query=chip+manufacturing&searchtype=all",
                    "https://arxiv.org/search/?query=EUV+lithography&searchtype=all",
                    "https://arxiv.org/search/?query=AI+chip+design&searchtype=all",
                ],
                source_type="research_papers"
            )
        
        # IEEE Xplore
        if config.enable_ieee_crawling:
            sources["ieee"] = SemiconductorDataSource(
                name="IEEE Xplore Semiconductor Papers",
                urls=[
                    "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=semiconductor%20manufacturing",
                    "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=AI%20chip%20design",
                    "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=lithography%20technology",
                ],
                source_type="research_papers"
            )
        
        # Semiconductor industry news
        if config.enable_semiconductor_news:
            sources["semiconductor_news"] = SemiconductorDataSource(
                name="Semiconductor Industry News",
                urls=[
                    "https://www.semiconductordigest.com/",
                    "https://semiengineering.com/",
                    "https://www.eetimes.com/category/semiconductors/",
                    "https://www.electronicsweekly.com/news/business/semiconductor/",
                    "https://www.anandtech.com/tag/semiconductors",
                ],
                source_type="news_articles"
            )
        
        # Patent databases
        if config.enable_patent_crawling:
            sources["patents"] = SemiconductorDataSource(
                name="Semiconductor Patents",
                urls=[
                    "https://patents.google.com/?q=semiconductor+manufacturing",
                    "https://patents.google.com/?q=chip+fabrication",
                    "https://patents.google.com/?q=lithography+process",
                ],
                source_type="patents"
            )
        
        # Industry reports
        if config.enable_industry_reports:
            sources["industry_reports"] = SemiconductorDataSource(
                name="Industry Reports",
                urls=[
                    "https://www.semiconductors.org/resources/",
                    "https://www.semi.org/en/connect/blog",
                    "https://www.mckinsey.com/industries/semiconductors",
                ],
                source_type="industry_reports"
            )
        
        return sources
    
    async def initialize_crawler(self):
        """Initialize the async web crawler"""
        if AsyncWebCrawler is None:
            logger.warning("crawl4ai not available, using fallback crawler")
            return
        
        try:
            self.crawler = AsyncWebCrawler(
                verbose=True,
                headless=True,
                browser_type="chromium",
                user_agent=config.user_agent,
                delay=config.crawl_delay,
            )
            await self.crawler.start()
            logger.info("Crawler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize crawler: {e}")
            raise
    
    async def crawl_sources(
        self, 
        source_filter: Optional[str] = None,
        update_existing: bool = False
    ):
        """Crawl all configured data sources"""
        if not self.crawler:
            await self.initialize_crawler()
        
        sources_to_crawl = self.data_sources
        if source_filter:
            sources_to_crawl = {
                k: v for k, v in self.data_sources.items() 
                if source_filter.lower() in k.lower()
            }
        
        for source_name, source in sources_to_crawl.items():
            if not update_existing and not source.should_crawl():
                logger.info(f"Skipping {source_name} - recently crawled")
                continue
            
            logger.info(f"Starting crawl for {source_name}")
            session_data = {
                "source_type": source_name,
                "start_time": datetime.now(),
                "status": "in_progress",
                "pages_crawled": 0,
                "documents_processed": 0,
                "errors": []
            }
            
            try:
                documents = await self._crawl_source(source)
                
                # Store documents in database
                if documents:
                    success = await db_manager.add_documents(
                        documents, 
                        collection_name=source.source_type
                    )
                    
                    if success:
                        session_data["documents_processed"] = len(documents)
                        session_data["status"] = "completed"
                        source.last_crawled = datetime.now()
                    else:
                        session_data["status"] = "failed"
                        session_data["errors"].append("Failed to store documents")
                else:
                    session_data["status"] = "no_data"
                
            except Exception as e:
                logger.error(f"Error crawling {source_name}: {e}")
                session_data["status"] = "error"
                session_data["errors"].append(str(e))
            
            finally:
                session_data["end_time"] = datetime.now()
                await db_manager.log_crawl_session(session_data)
    
    async def _crawl_source(self, source: SemiconductorDataSource) -> List[Dict[str, Any]]:
        """Crawl a specific data source"""
        documents = []
        
        for url in source.urls[:config.max_pages_per_source]:
            try:
                # Configure extraction strategy for semiconductor content
                extraction_strategy = self._get_extraction_strategy(source.source_type)
                
                result = await self.crawler.arun(
                    url=url,
                    extraction_strategy=extraction_strategy,
                    bypass_cache=True,
                    css_selector="article, .content, .paper-content, main, .main-content",
                    word_count_threshold=50,
                    excluded_tags=['nav', 'footer', 'header', 'sidebar', 'advertisement'],
                    remove_overlay_elements=True,
                )
                
                if result.success and result.extracted_content:
                    document = {
                        "id": f"{source.name}_{hash(url)}_{datetime.now().timestamp()}",
                        "content": result.extracted_content,
                        "source": source.name,
                        "url": url,
                        "title": getattr(result, 'title', ''),
                        "timestamp": datetime.now().isoformat(),
                        "type": source.source_type,
                        "metadata": {
                            "word_count": len(result.extracted_content.split()),
                            "crawl_timestamp": datetime.now().isoformat(),
                            "source_type": source.source_type,
                        }
                    }
                    documents.append(document)
                    
                    logger.info(f"Successfully crawled: {url}")
                
                # Respect rate limiting
                await asyncio.sleep(config.crawl_delay)
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                continue
        
        return documents
    
    def _get_extraction_strategy(self, source_type: str):
        """Get appropriate extraction strategy based on source type"""
        if LLMExtractionStrategy is None:
            return None
        
        strategies = {
            "research_papers": LLMExtractionStrategy(
                provider="openai",
                api_token=config.openai_api_key,
                instruction="""
                Extract key information about semiconductor research including:
                - Main technological innovations or breakthroughs
                - Manufacturing processes discussed
                - AI applications in semiconductor design/manufacturing
                - Historical context and timeline information
                - Performance metrics and technical specifications
                - Future trends and predictions
                
                Focus on factual, technical content and preserve important numerical data.
                """
            ),
            "news_articles": LLMExtractionStrategy(
                provider="openai",
                api_token=config.openai_api_key,
                instruction="""
                Extract semiconductor industry news focusing on:
                - Major announcements from chip manufacturers
                - New manufacturing technologies and processes
                - AI integration in semiconductor industry
                - Market trends and business developments
                - Regulatory changes affecting the industry
                - Historical milestones and company developments
                
                Preserve dates, company names, and quantitative information.
                """
            ),
            "patents": LLMExtractionStrategy(
                provider="openai",
                api_token=config.openai_api_key,
                instruction="""
                Extract patent information related to semiconductors:
                - Patent title and abstract
                - Key technical innovations described
                - Manufacturing process improvements
                - AI-related semiconductor technologies
                - Filing dates and inventors
                - Technical specifications and claims
                
                Focus on technical details and innovation descriptions.
                """
            ),
            "industry_reports": LLMExtractionStrategy(
                provider="openai",
                api_token=config.openai_api_key,
                instruction="""
                Extract industry report content about semiconductors:
                - Market analysis and forecasts
                - Technological roadmaps and trends
                - Manufacturing capacity and investments
                - AI impact on semiconductor industry
                - Historical analysis of industry evolution
                - Competitive landscape information
                
                Preserve statistical data, dates, and quantitative projections.
                """
            )
        }
        
        return strategies.get(source_type)
    
    async def get_crawl_statistics(self) -> Dict[str, Any]:
        """Get crawling statistics"""
        stats = {
            "total_sources": len(self.data_sources),
            "active_sources": len([s for s in self.data_sources.values() if s.should_crawl()]),
            "last_crawl_times": {
                name: source.last_crawled.isoformat() if source.last_crawled else None
                for name, source in self.data_sources.items()
            }
        }
        
        # Add database statistics
        db_stats = await db_manager.get_system_stats()
        stats.update(db_stats)
        
        return stats
    
    async def close(self):
        """Close crawler resources"""
        if self.crawler:
            await self.crawler.close()
            logger.info("Crawler closed")

# Global crawler manager instance
crawler_manager = CrawlerManager()
