"""
RAG Query Engine for semiconductor knowledge retrieval
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, NamedTuple
import json

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from sentence_transformers import SentenceTransformer
    import openai
except ImportError:
    RecursiveCharacterTextSplitter = None
    Document = None
    SentenceTransformer = None
    openai = None

from core.config import config
from core.database import db_manager

logger = logging.getLogger(__name__)

class QueryResponse(NamedTuple):
    """Response from the query engine"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    processing_time: float

class RAGQueryEngine:
    """Main query engine for the RAG system"""
    
    def __init__(self):
        self.embedding_model = None
        self.text_splitter = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize the embedding and text processing models"""
        try:
            if SentenceTransformer:
                self.embedding_model = SentenceTransformer(config.embedding_model)
                logger.info(f"Loaded embedding model: {config.embedding_model}")
            
            if RecursiveCharacterTextSplitter:
                self.text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap,
                    separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
                )
                logger.info("Text splitter initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
    
    async def query(
        self, 
        question: str, 
        include_sources: bool = True,
        max_sources: int = 10,
        collections: Optional[List[str]] = None
    ) -> QueryResponse:
        """
        Query the knowledge base for semiconductor information
        
        Args:
            question: The question to ask
            include_sources: Whether to include source documents
            max_sources: Maximum number of source documents to return
            collections: Specific collections to search (defaults to all)
        
        Returns:
            QueryResponse with answer and sources
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Retrieve relevant documents
            relevant_docs = await self._retrieve_documents(
                question, 
                max_sources=max_sources,
                collections=collections
            )
            
            if not relevant_docs:
                return QueryResponse(
                    answer="I don't have enough information to answer that question about semiconductor manufacturing. Please try rephrasing your question or check if the knowledge base has been updated recently.",
                    sources=[],
                    confidence=0.0,
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Step 2: Generate answer using RAG
            answer = await self._generate_answer(question, relevant_docs)
            
            # Step 3: Calculate confidence score
            confidence = self._calculate_confidence(relevant_docs, answer)
            
            # Step 4: Prepare sources if requested
            sources = relevant_docs if include_sources else []
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return QueryResponse(
                answer=answer,
                sources=sources,
                confidence=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryResponse(
                answer=f"I encountered an error while processing your question: {str(e)}",
                sources=[],
                confidence=0.0,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _retrieve_documents(
        self, 
        query: str, 
        max_sources: int = 10,
        collections: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from the knowledge base"""
        
        # Default collections if none specified
        if collections is None:
            collections = ["documents", "research_papers", "news_articles", "patents", "historical_data"]
        
        all_results = []
        
        # Query each collection
        for collection_name in collections:
            try:
                results = await db_manager.query_documents(
                    query_text=query,
                    collection_name=collection_name,
                    n_results=max_sources // len(collections) + 2  # Get a few extra per collection
                )
                
                # Add collection info to results
                for result in results:
                    result["collection"] = collection_name
                    all_results.append(result)
                    
            except Exception as e:
                logger.warning(f"Error querying collection {collection_name}: {e}")
                continue
        
        # Sort by relevance score and take top results
        all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Filter by similarity threshold
        filtered_results = [
            result for result in all_results
            if result.get("relevance_score", 0) >= config.similarity_threshold
        ]
        
        return filtered_results[:max_sources]
    
    async def _generate_answer(self, question: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate an answer using the retrieved context"""
        
        if not openai or not config.openai_api_key:
            # Fallback to simple context-based response
            return self._generate_fallback_answer(question, context_docs)
        
        try:
            # Prepare context from retrieved documents
            context = self._prepare_context(context_docs)
            
            # Create system prompt for semiconductor expertise
            system_prompt = """You are an expert in semiconductor manufacturing and technology with deep knowledge of:
- Semiconductor fabrication processes and evolution over the last 30 years
- AI applications in chip design and manufacturing
- Historical technological milestones in the semiconductor industry
- Current trends and future directions in semiconductor technology

Your responses should be:
- Technically accurate and detailed
- Based on the provided context documents
- Include historical perspective when relevant
- Mention specific years, companies, and technologies when available
- Acknowledge if information is limited or uncertain

Always cite the most relevant sources from the context when providing your answer."""

            user_prompt = f"""Based on the following context about semiconductor manufacturing and technology, please answer this question: {question}

Context:
{context}

Please provide a comprehensive answer that includes:
1. Direct answer to the question
2. Historical context if relevant
3. Current state of the technology
4. Future implications if applicable
5. Specific examples and data points from the sources"""

            # Use OpenAI to generate response
            client = openai.OpenAI(api_key=config.openai_api_key)
            
            response = client.chat.completions.create(
                model=config.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=config.openai_temperature,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer with OpenAI: {e}")
            return self._generate_fallback_answer(question, context_docs)
    
    def _generate_fallback_answer(self, question: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate a fallback answer when LLM is not available"""
        
        if not context_docs:
            return "I don't have relevant information to answer your question about semiconductor manufacturing."
        
        # Simple extractive approach - find most relevant chunks
        relevant_text = []
        for doc in context_docs[:3]:  # Use top 3 most relevant docs
            content = doc.get("content", "")
            if len(content) > 200:
                # Take first part of content
                relevant_text.append(content[:500] + "...")
            else:
                relevant_text.append(content)
        
        answer = f"Based on the available information about semiconductor manufacturing:\n\n"
        answer += "\n\n".join(relevant_text)
        
        # Add source information
        sources = []
        for doc in context_docs[:3]:
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown source")
            if source not in sources:
                sources.append(source)
        
        if sources:
            answer += f"\n\nSources: {', '.join(sources)}"
        
        return answer
    
    def _prepare_context(self, docs: List[Dict[str, Any]], max_length: int = 4000) -> str:
        """Prepare context string from retrieved documents"""
        context_parts = []
        current_length = 0
        
        for doc in docs:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # Add source information
            source_info = f"Source: {metadata.get('source', 'Unknown')}"
            if metadata.get("title"):
                source_info += f" - {metadata['title']}"
            if metadata.get("timestamp"):
                source_info += f" ({metadata['timestamp'][:10]})"  # Just the date
            
            doc_text = f"{source_info}\n{content}\n"
            
            if current_length + len(doc_text) > max_length:
                # Truncate if needed
                remaining_space = max_length - current_length
                if remaining_space > 100:  # Only add if there's meaningful space
                    doc_text = doc_text[:remaining_space] + "..."
                    context_parts.append(doc_text)
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        return "\n---\n".join(context_parts)
    
    def _calculate_confidence(self, docs: List[Dict[str, Any]], answer: str) -> float:
        """Calculate confidence score for the answer"""
        if not docs:
            return 0.0
        
        # Basic confidence calculation based on:
        # 1. Number of relevant documents
        # 2. Average relevance score
        # 3. Answer length (longer = more detailed = higher confidence)
        
        num_docs = len(docs)
        avg_relevance = sum(doc.get("relevance_score", 0) for doc in docs) / num_docs
        answer_length_factor = min(len(answer) / 500, 1.0)  # Normalize to 0-1
        
        # Weighted combination
        confidence = (
            (num_docs / 10) * 0.3 +  # Number of docs (max 10)
            avg_relevance * 0.5 +     # Average relevance
            answer_length_factor * 0.2 # Answer completeness
        )
        
        return min(confidence, 1.0)
    
    async def get_historical_timeline(self, topic: str = "semiconductor manufacturing") -> Dict[str, Any]:
        """Get a historical timeline for a specific semiconductor topic"""
        
        # Query for historical information
        query = f"historical timeline evolution development {topic} years decades milestones"
        
        docs = await self._retrieve_documents(query, max_sources=20)
        
        # Extract timeline information
        timeline_events = []
        for doc in docs:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # Simple year extraction (this could be more sophisticated)
            import re
            years = re.findall(r'\b(19[5-9]\d|20[0-2]\d)\b', content)
            
            for year in set(years):  # Remove duplicates
                timeline_events.append({
                    "year": int(year),
                    "content": content[:200] + "...",
                    "source": metadata.get("source", "Unknown"),
                    "relevance": doc.get("relevance_score", 0)
                })
        
        # Sort by year
        timeline_events.sort(key=lambda x: x["year"])
        
        return {
            "topic": topic,
            "timeline": timeline_events,
            "total_events": len(timeline_events),
            "year_range": {
                "start": timeline_events[0]["year"] if timeline_events else None,
                "end": timeline_events[-1]["year"] if timeline_events else None
            }
        }

# Global query engine instance
class QueryEngine(RAGQueryEngine):
    """Alias for backward compatibility"""
    pass

query_engine = QueryEngine()
