"""
Streamlit Demo for Semiconductor Learning System
Simplified version for cloud deployment without ChromaDB dependencies
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import time
import json
from typing import Dict, List, Optional
import requests
from dataclasses import dataclass

# Configure Streamlit page
st.set_page_config(
    page_title="🔬 Semiconductor Learning System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/thegeekybeng/semiconductor-learning-system',
        'Report a bug': 'https://github.com/thegeekybeng/semiconductor-learning-system/issues',
        'About': "# Semiconductor Learning System\nAI-powered system for semiconductor manufacturing knowledge"
    }
)

# Initialize OpenAI client if API key is available
try:
    import openai
    openai_client = None
    api_key = os.getenv('OPENAI_API_KEY') or st.secrets.get('OPENAI_API_KEY')
    if api_key:
        openai_client = openai.OpenAI(api_key=api_key)
except Exception as e:
    openai_client = None
    st.warning(f"OpenAI not available: {e}")

# Sample data for demo purposes
@dataclass
class KnowledgeEntry:
    title: str
    content: str
    source: str
    date: datetime
    category: str
    relevance_score: float = 0.85

# Sample semiconductor knowledge base
SAMPLE_KNOWLEDGE = [
    KnowledgeEntry(
        title="EUV Lithography Advances in 2024",
        content="Extreme ultraviolet (EUV) lithography has reached new milestones with improved power sources and enhanced resist materials, enabling sub-3nm manufacturing processes.",
        source="IEEE Spectrum",
        date=datetime(2024, 6, 15),
        category="Manufacturing",
        relevance_score=0.92
    ),
    KnowledgeEntry(
        title="AI-Driven Chip Design Optimization",
        content="Machine learning algorithms are revolutionizing chip layout optimization, reducing design time by 40% while improving performance metrics.",
        source="Nature Electronics",
        date=datetime(2024, 8, 20),
        category="AI/ML",
        relevance_score=0.88
    ),
    KnowledgeEntry(
        title="3D NAND Flash Memory Breakthrough",
        content="New 3D NAND architectures with 200+ layers demonstrate significant improvements in storage density and read/write speeds.",
        source="AnandTech",
        date=datetime(2024, 9, 10),
        category="Memory",
        relevance_score=0.85
    ),
    KnowledgeEntry(
        title="Quantum Dot Manufacturing Techniques",
        content="Advanced quantum dot synthesis methods enable precise control over size distribution, crucial for next-generation display and quantum computing applications.",
        source="Advanced Materials",
        date=datetime(2024, 7, 5),
        category="Quantum",
        relevance_score=0.90
    ),
    KnowledgeEntry(
        title="Chiplet Architecture Evolution",
        content="Heterogeneous integration through chiplet design is becoming the dominant approach for high-performance computing systems, offering better yields and modularity.",
        source="Semiconductor Today",
        date=datetime(2024, 5, 25),
        category="Architecture",
        relevance_score=0.87
    )
]

def simulate_rag_query(query: str) -> Dict:
    """Simulate RAG query processing"""
    # Simple keyword matching for demo
    query_lower = query.lower()
    results = []
    
    for entry in SAMPLE_KNOWLEDGE:
        score = 0
        if any(word in entry.content.lower() for word in query_lower.split()):
            score += 0.3
        if any(word in entry.title.lower() for word in query_lower.split()):
            score += 0.5
        if entry.category.lower() in query_lower:
            score += 0.4
            
        if score > 0:
            results.append({
                'entry': entry,
                'relevance': min(score, 1.0)
            })
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance'], reverse=True)
    
    return {
        'query': query,
        'results': results[:5],  # Top 5 results
        'total_found': len(results),
        'processing_time': np.random.uniform(0.2, 0.8)
    }

def generate_ai_response(query: str, context_entries: List[KnowledgeEntry]) -> str:
    """Generate AI response using OpenAI or fallback to template"""
    if openai_client:
        try:
            context = "\n".join([f"- {entry.title}: {entry.content}" for entry in context_entries])
            
            messages = [
                {"role": "system", "content": "You are an expert in semiconductor manufacturing and technology. Provide detailed, technical responses based on the provided context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nPlease provide a comprehensive answer based on the context above."}
            ]
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,  # type: ignore
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content or "No response generated"
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
    
    # Fallback response
    if context_entries:
        return f"""Based on the knowledge base, here's what I found about "{query}":

{context_entries[0].content}

This information comes from {context_entries[0].source} and relates to {context_entries[0].category} in semiconductor technology. The semiconductor industry continues to evolve rapidly with innovations in manufacturing processes, materials science, and design methodologies.

Key trends include:
- Advanced lithography techniques (EUV, next-gen)
- AI-driven design optimization
- 3D integration and chiplet architectures
- Novel materials and quantum technologies

For more detailed analysis, please ensure OpenAI API key is configured."""
    else:
        return f"""I couldn't find specific information about "{query}" in the current knowledge base. However, I can provide some general insights:

The semiconductor industry is rapidly evolving with several key focus areas:
- Manufacturing process improvements (EUV lithography, advanced nodes)
- AI/ML integration in design and manufacturing
- Memory technology advances (3D NAND, emerging memories)
- Quantum computing and photonics integration

To get more specific information, try queries related to:
- Manufacturing processes
- Memory technologies
- AI in semiconductors
- Quantum computing
- Chip architecture"""

def create_system_metrics():
    """Create sample system metrics for monitoring dashboard"""
    return {
        'cpu_usage': np.random.uniform(20, 80),
        'memory_usage': np.random.uniform(30, 70),
        'storage_usage': np.random.uniform(40, 60),
        'active_crawlers': np.random.randint(2, 8),
        'knowledge_entries': len(SAMPLE_KNOWLEDGE) * np.random.randint(800, 1200),
        'daily_queries': np.random.randint(150, 350),
        'api_response_time': np.random.uniform(0.2, 1.5),
        'last_update': datetime.now() - timedelta(minutes=np.random.randint(5, 60))
    }

# Main Streamlit App
def main():
    # Sidebar navigation
    st.sidebar.title("🔬 Navigation")
    pages = {
        "🏠 Dashboard": "dashboard",
        "🤖 RAG Query": "rag_query", 
        "📚 Knowledge Base": "knowledge_base",
        "🕷️ Web Crawling": "web_crawling",
        "📊 System Monitor": "system_monitor",
        "📈 Analytics": "analytics"
    }
    
    selected_page = st.sidebar.radio("Select Page", list(pages.keys()))
    page_id = pages[selected_page]
    
    # API Configuration in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuration")
    
    if openai_client:
        st.sidebar.success("✅ OpenAI API Connected")
    else:
        st.sidebar.warning("⚠️ OpenAI API Not Connected")
        st.sidebar.info("Add OPENAI_API_KEY to Streamlit secrets for full functionality")
    
    # Main content area
    if page_id == "dashboard":
        show_dashboard()
    elif page_id == "rag_query":
        show_rag_query()
    elif page_id == "knowledge_base":
        show_knowledge_base()
    elif page_id == "web_crawling":
        show_web_crawling()
    elif page_id == "system_monitor":
        show_system_monitor()
    elif page_id == "analytics":
        show_analytics()

def show_dashboard():
    st.title("🔬 Semiconductor Learning System Dashboard")
    st.markdown("Welcome to the AI-powered semiconductor manufacturing knowledge system!")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    metrics = create_system_metrics()
    
    with col1:
        st.metric("Knowledge Entries", f"{metrics['knowledge_entries']:,}", "+127 today")
    with col2:
        st.metric("Daily Queries", metrics['daily_queries'], "+23 vs yesterday")
    with col3:
        st.metric("Active Crawlers", metrics['active_crawlers'], "All systems operational")
    with col4:
        st.metric("Avg Response Time", f"{metrics['api_response_time']:.2f}s", "-0.3s improvement")
    
    # System overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 System Activity (Last 24h)")
        # Generate sample activity data
        hours = list(range(24))
        queries = [np.random.randint(5, 25) for _ in hours]
        crawl_activity = [np.random.randint(2, 12) for _ in hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=queries, mode='lines+markers', name='Queries', line=dict(color='#FF6B6B')))
        fig.add_trace(go.Scatter(x=hours, y=crawl_activity, mode='lines+markers', name='Crawl Activity', line=dict(color='#4ECDC4')))
        fig.update_layout(title="Hourly Activity", xaxis_title="Hour", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Knowledge Categories")
        categories = ['Manufacturing', 'AI/ML', 'Memory', 'Quantum', 'Architecture', 'Materials', 'Testing']
        counts = [np.random.randint(50, 200) for _ in categories]
        
        fig = px.pie(values=counts, names=categories, color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent updates
    st.subheader("🔄 Recent Knowledge Updates")
    for entry in SAMPLE_KNOWLEDGE[:3]:
        with st.expander(f"📄 {entry.title} - {entry.source}"):
            st.write(entry.content)
            st.caption(f"Category: {entry.category} | Date: {entry.date.strftime('%Y-%m-%d')}")

def show_rag_query():
    st.title("🤖 RAG Query Interface")
    st.markdown("Ask questions about semiconductor manufacturing and technology!")
    
    # Query input
    query = st.text_input("Enter your question:", placeholder="e.g., What are the latest advances in EUV lithography?")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 Search", type="primary")
    
    if search_button and query:
        with st.spinner("Processing your query..."):
            # Simulate processing time
            time.sleep(1)
            
            # Get query results
            results = simulate_rag_query(query)
            
            st.success(f"Found {results['total_found']} relevant entries in {results['processing_time']:.2f} seconds")
            
            # Display results
            if results['results']:
                st.subheader("📚 Relevant Knowledge")
                
                # Get context for AI response
                context_entries = [r['entry'] for r in results['results'][:3]]
                
                # Generate AI response
                with st.spinner("Generating AI response..."):
                    ai_response = generate_ai_response(query, context_entries)
                
                # Display AI response
                st.subheader("🤖 AI Response")
                st.write(ai_response)
                
                # Display source documents
                st.subheader("📖 Source Documents")
                for i, result in enumerate(results['results']):
                    entry = result['entry']
                    relevance = result['relevance']
                    
                    with st.expander(f"📄 {entry.title} (Relevance: {relevance:.2f})"):
                        st.write(entry.content)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption(f"**Source:** {entry.source}")
                        with col2:
                            st.caption(f"**Category:** {entry.category}")
                        with col3:
                            st.caption(f"**Date:** {entry.date.strftime('%Y-%m-%d')}")
            else:
                st.warning("No relevant documents found. Try rephrasing your query.")
    
    # Example queries
    st.subheader("💡 Example Queries")
    examples = [
        "What are the latest advances in EUV lithography?",
        "How is AI being used in chip design?",
        "What are the benefits of chiplet architecture?",
        "Tell me about 3D NAND memory technology",
        "What is quantum dot manufacturing?"
    ]
    
    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(f"💭 {example}", key=f"example_{i}"):
                st.rerun()

def show_knowledge_base():
    st.title("📚 Knowledge Base Management")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search knowledge base:", placeholder="Search titles, content, or sources...")
    with col2:
        category_filter = st.selectbox("Filter by category:", ["All"] + list(set(entry.category for entry in SAMPLE_KNOWLEDGE)))
    
    # Filter entries
    filtered_entries = SAMPLE_KNOWLEDGE
    if search_term:
        filtered_entries = [
            entry for entry in filtered_entries 
            if search_term.lower() in entry.title.lower() or 
               search_term.lower() in entry.content.lower() or 
               search_term.lower() in entry.source.lower()
        ]
    
    if category_filter != "All":
        filtered_entries = [entry for entry in filtered_entries if entry.category == category_filter]
    
    # Display results
    st.subheader(f"📊 Showing {len(filtered_entries)} entries")
    
    for i, entry in enumerate(filtered_entries):
        with st.expander(f"📄 {entry.title}", expanded=(i == 0)):
            st.write(entry.content)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.caption(f"**Source:** {entry.source}")
            with col2:
                st.caption(f"**Category:** {entry.category}")
            with col3:
                st.caption(f"**Date:** {entry.date.strftime('%Y-%m-%d')}")
            with col4:
                st.caption(f"**Relevance:** {entry.relevance_score:.2f}")

def show_web_crawling():
    st.title("🕷️ Web Crawling Dashboard")
    
    # Crawling controls
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("▶️ Start Crawlers", type="primary")
    with col2:
        st.button("⏸️ Pause Crawlers")
    with col3:
        st.button("🔄 Refresh Status")
    
    # Crawler status
    st.subheader("📊 Crawler Status")
    
    crawlers = [
        {"name": "ArXiv Papers", "status": "Active", "last_run": "2 minutes ago", "documents": 1247},
        {"name": "IEEE Xplore", "status": "Active", "last_run": "5 minutes ago", "documents": 892},
        {"name": "Semiconductor Today", "status": "Idle", "last_run": "1 hour ago", "documents": 456},
        {"name": "Nature Electronics", "status": "Active", "last_run": "8 minutes ago", "documents": 234},
        {"name": "AnandTech", "status": "Error", "last_run": "3 hours ago", "documents": 187}
    ]
    
    for crawler in crawlers:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write(f"**{crawler['name']}**")
        with col2:
            if crawler['status'] == 'Active':
                st.success(f"🟢 {crawler['status']}")
            elif crawler['status'] == 'Idle':
                st.warning(f"🟡 {crawler['status']}")
            else:
                st.error(f"🔴 {crawler['status']}")
        with col3:
            st.write(crawler['last_run'])
        with col4:
            st.write(f"{crawler['documents']} docs")
    
    # Crawling activity chart
    st.subheader("📈 Crawling Activity (Last 7 Days)")
    days = pd.date_range(end=datetime.now(), periods=7).strftime('%Y-%m-%d')
    activity = [np.random.randint(20, 100) for _ in days]
    
    fig = px.bar(x=days, y=activity, title="Documents Crawled Per Day")
    fig.update_layout(xaxis_title="Date", yaxis_title="Documents")
    st.plotly_chart(fig, use_container_width=True)

def show_system_monitor():
    st.title("📊 System Monitor")
    
    # Real-time metrics
    metrics = create_system_metrics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CPU Usage", f"{metrics['cpu_usage']:.1f}%", "Normal")
    with col2:
        st.metric("Memory Usage", f"{metrics['memory_usage']:.1f}%", "Good")
    with col3:
        st.metric("Storage Usage", f"{metrics['storage_usage']:.1f}%", "Optimal")
    
    # System health charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💾 Resource Usage")
        labels = ['CPU', 'Memory', 'Storage', 'Network']
        values = [metrics['cpu_usage'], metrics['memory_usage'], metrics['storage_usage'], np.random.uniform(10, 40)]
        
        fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])])
        fig.update_layout(title="Current Resource Usage (%)", yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🔄 API Performance")
        time_points = list(range(24))
        response_times = [np.random.uniform(0.1, 2.0) for _ in time_points]
        
        fig = go.Figure(data=go.Scatter(x=time_points, y=response_times, mode='lines+markers', line=dict(color='#FF6B6B')))
        fig.update_layout(title="Response Time (Last 24h)", xaxis_title="Hour", yaxis_title="Seconds")
        st.plotly_chart(fig, use_container_width=True)
    
    # System logs
    st.subheader("📝 Recent System Logs")
    logs = [
        {"time": "2024-07-28 10:32:15", "level": "INFO", "message": "RAG query processed successfully"},
        {"time": "2024-07-28 10:31:45", "level": "INFO", "message": "Web crawler completed ArXiv scan"},
        {"time": "2024-07-28 10:30:22", "level": "WARNING", "message": "High memory usage detected"},
        {"time": "2024-07-28 10:29:10", "level": "INFO", "message": "Knowledge base updated with 15 new entries"},
        {"time": "2024-07-28 10:28:03", "level": "ERROR", "message": "Connection timeout to IEEE Xplore"}
    ]
    
    for log in logs:
        col1, col2, col3 = st.columns([2, 1, 5])
        with col1:
            st.text(log['time'])
        with col2:
            if log['level'] == 'ERROR':
                st.error(log['level'])
            elif log['level'] == 'WARNING':
                st.warning(log['level'])
            else:
                st.info(log['level'])
        with col3:
            st.text(log['message'])

def show_analytics():
    st.title("📈 Analytics Dashboard")
    
    # Usage analytics
    st.subheader("📊 Usage Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Query trends
        dates = pd.date_range(end=datetime.now(), periods=30).strftime('%Y-%m-%d')
        queries = [np.random.randint(50, 200) for _ in dates]
        
        fig = px.line(x=dates, y=queries, title="Daily Query Volume (Last 30 Days)")
        fig.update_layout(xaxis_title="Date", yaxis_title="Queries")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Knowledge growth
        knowledge_growth = np.cumsum([np.random.randint(10, 50) for _ in dates])
        
        fig = px.area(x=dates, y=knowledge_growth, title="Knowledge Base Growth")
        fig.update_layout(xaxis_title="Date", yaxis_title="Total Documents")
        st.plotly_chart(fig, use_container_width=True)
    
    # Topic analysis
    st.subheader("🏷️ Popular Topics")
    
    topics = ['EUV Lithography', 'AI Chip Design', '3D NAND', 'Quantum Computing', 'Chiplet Architecture', 'Memory Technology']
    popularity = [np.random.randint(20, 100) for _ in topics]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(x=topics, y=popularity, title="Topic Popularity (Query Count)")
        fig.update_layout(xaxis_title="Topic", yaxis_title="Queries")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # User engagement metrics
        st.metric("Avg Session Duration", "12.5 min", "+2.3 min")
        st.metric("Queries per Session", "4.2", "+0.8")
        st.metric("User Satisfaction", "4.6/5.0", "+0.2")
        st.metric("Knowledge Accuracy", "94.2%", "+1.1%")

if __name__ == "__main__":
    main()
