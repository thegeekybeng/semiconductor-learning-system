"""
Streamlit Demo Application for Semiconductor Learning System
A comprehensive web interface showcasing all system capabilities
"""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our system components
try:
    from core.config import config
    from core.database import db_manager
    from core.system_monitor import system_monitor
    from rag.query_engine import query_engine
    from crawlers.crawler_manager import crawler_manager
    from models.training_manager import training_manager
except ImportError as e:
    st.error(f"Failed to import system components: {e}")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="Semiconductor Learning System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .sidebar-section {
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_system():
    """Initialize the system components"""
    try:
        # This would normally be done asynchronously, but for demo purposes
        # we'll simulate the initialization
        return True
    except Exception as e:
        st.error(f"System initialization failed: {e}")
        return False

def run_async(func):
    """Helper to run async functions in Streamlit"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already a running loop, create a new one in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, func)
                return future.result()
        else:
            return loop.run_until_complete(func)
    except RuntimeError:
        return asyncio.run(func)

def get_system_status():
    """Get current system status"""
    try:
        status = system_monitor.get_system_status()
        return status
    except Exception as e:
        return {"error": str(e)}

def format_status_display(status_value):
    """Format status for display with colors"""
    if status_value == "healthy":
        return f'<span class="status-healthy">✅ Healthy</span>'
    elif status_value == "warning":
        return f'<span class="status-warning">⚠️ Warning</span>'
    elif status_value == "error":
        return f'<span class="status-error">❌ Error</span>'
    else:
        return f'<span class="status-warning">❓ {status_value}</span>'

def create_sample_data():
    """Create sample data for demonstration"""
    sample_documents = [
        {
            "title": "EUV Lithography: Principles and Applications",
            "content": "Extreme ultraviolet (EUV) lithography represents a significant advancement in semiconductor manufacturing technology. Operating at a wavelength of 13.5 nm, EUV enables the production of smaller feature sizes essential for advanced node processes including 7nm, 5nm, and 3nm technologies. The technology addresses critical challenges in pattern resolution and overlay accuracy that traditional deep ultraviolet (DUV) lithography cannot achieve at these scales.",
            "source": "IEEE Transactions on Semiconductor Manufacturing",
            "date": "2024-01-15",
            "topics": ["EUV", "lithography", "semiconductor manufacturing"]
        },
        {
            "title": "AI-Driven Yield Optimization in Semiconductor Fabs",
            "content": "Machine learning algorithms are revolutionizing semiconductor manufacturing by enabling predictive maintenance, defect detection, and yield optimization. Advanced neural networks can analyze vast amounts of process data to identify patterns and anomalies that human operators might miss. This leads to improved production efficiency, reduced waste, and higher quality chips.",
            "source": "Nature Electronics",
            "date": "2024-02-10",
            "topics": ["AI", "yield optimization", "machine learning", "semiconductor"]
        },
        {
            "title": "3nm Process Node: Challenges and Breakthroughs",
            "content": "The transition to 3nm process technology represents one of the most challenging advancements in semiconductor history. Key challenges include gate-all-around (GAA) transistor implementation, extreme ultraviolet lithography optimization, and advanced packaging techniques. Leading foundries like TSMC and Samsung have made significant investments in overcoming these technical hurdles.",
            "source": "Semiconductor Industry Association",
            "date": "2024-03-05",
            "topics": ["3nm", "process node", "GAA", "TSMC", "Samsung"]
        }
    ]
    return sample_documents

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔬 Semiconductor Learning System</h1>', unsafe_allow_html=True)
    st.markdown("### Advanced AI-Powered Knowledge Management for Semiconductor Manufacturing")
    
    # Sidebar navigation
    st.sidebar.markdown("## 🎛️ Navigation")
    page = st.sidebar.selectbox(
        "Select a page:",
        ["🏠 Dashboard", "🤖 RAG Query System", "📊 Knowledge Base", "🕷️ Web Crawling", "🔧 System Monitor", "📈 Analytics"]
    )
    
    # Initialize system status
    if 'system_initialized' not in st.session_state:
        with st.spinner("Initializing system..."):
            st.session_state.system_initialized = initialize_system()
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🤖 RAG Query System":
        show_rag_system()
    elif page == "📊 Knowledge Base":
        show_knowledge_base()
    elif page == "🕷️ Web Crawling":
        show_crawling_interface()
    elif page == "🔧 System Monitor":
        show_system_monitor()
    elif page == "📈 Analytics":
        show_analytics()

def show_dashboard():
    """Show main dashboard"""
    st.header("📊 System Dashboard")
    
    # System status overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🟢 System Status",
            value="Operational",
            delta="All systems active"
        )
    
    with col2:
        st.metric(
            label="📚 Documents",
            value="156",
            delta="+12 today"
        )
    
    with col3:
        st.metric(
            label="🔍 Queries Today",
            value="47",
            delta="+15 vs yesterday"
        )
    
    with col4:
        st.metric(
            label="⚡ Avg Response",
            value="0.8s",
            delta="-0.2s improvement"
        )
    
    st.divider()
    
    # Recent activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Query Volume Trend")
        # Create sample data for the chart
        dates = pd.date_range(start='2024-07-20', end='2024-07-28', freq='D')
        queries = [23, 31, 28, 45, 52, 38, 47, 42, 47]
        
        fig = px.line(
            x=dates[:len(queries)], 
            y=queries,
            title="Daily Query Volume",
            labels={'x': 'Date', 'y': 'Number of Queries'}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📂 Knowledge Base Growth")
        categories = ['Research Papers', 'Industry Reports', 'News Articles', 'Patents', 'Technical Docs']
        values = [45, 28, 35, 18, 30]
        
        fig = px.pie(
            values=values,
            names=categories,
            title="Document Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # System health indicators
    st.subheader("🏥 System Health")
    health_col1, health_col2, health_col3 = st.columns(3)
    
    with health_col1:
        st.markdown("**🔗 API Connectivity**")
        st.success("OpenAI API: Connected")
        st.info("ChromaDB: Active")
        st.success("System Monitor: Running")
    
    with health_col2:
        st.markdown("**💾 Storage Status**")
        st.info("Vector DB Size: 16.2 MB")
        st.success("Disk Space: 85% free")
        st.success("Memory Usage: Normal")
    
    with health_col3:
        st.markdown("**🔄 Background Tasks**")
        st.success("Scheduled Crawling: Active")
        st.info("Model Training: Pending")
        st.success("Health Monitoring: Running")

def show_rag_system():
    """Show RAG query interface"""
    st.header("🤖 RAG Query System")
    st.markdown("Ask questions about semiconductor manufacturing, and get AI-powered answers backed by industry knowledge.")
    
    # Query interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_query = st.text_area(
            "Enter your question:",
            placeholder="e.g., What are the main challenges in EUV lithography?",
            height=100
        )
    
    with col2:
        st.markdown("**Query Options:**")
        include_sources = st.checkbox("Include sources", value=True)
        max_sources = st.slider("Max sources", 1, 20, 5)
        confidence_threshold = st.slider("Confidence threshold", 0.0, 1.0, 0.7)
    
    if st.button("🔍 Query System", type="primary"):
        if user_query.strip():
            with st.spinner("Processing your query..."):
                # Simulate query processing
                time.sleep(2)
                
                # Mock response for demonstration
                response = simulate_rag_response(user_query)
                
                st.subheader("📖 Answer")
                st.write(response['answer'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Confidence Score", f"{response['confidence']:.2f}")
                with col2:
                    st.metric("Processing Time", f"{response['processing_time']:.3f}s")
                
                if include_sources and response['sources']:
                    st.subheader("📚 Sources")
                    for i, source in enumerate(response['sources'][:max_sources], 1):
                        with st.expander(f"Source {i}: {source['title']}"):
                            st.write(f"**Source:** {source['source']}")
                            st.write(f"**Date:** {source['date']}")
                            st.write(f"**Relevance:** {source['relevance']:.2f}")
                            st.write(source['excerpt'])
        else:
            st.warning("Please enter a question to query the system.")
    
    # Sample queries
    st.subheader("💡 Sample Queries")
    sample_queries = [
        "What is EUV lithography and why is it important?",
        "How has semiconductor manufacturing evolved over the past 30 years?",
        "What are the main challenges in 3nm process node development?",
        "How does AI improve semiconductor yield optimization?",
        "What are the key differences between TSMC and Samsung's 3nm processes?"
    ]
    
    for query in sample_queries:
        if st.button(f"📝 {query}", key=f"sample_{hash(query)}"):
            st.text_area("Query:", value=query, height=60, key=f"demo_query_{hash(query)}")

def simulate_rag_response(query):
    """Simulate a RAG response for demonstration"""
    sample_responses = {
        "euv lithography": {
            "answer": "EUV (Extreme Ultraviolet) lithography is a cutting-edge semiconductor manufacturing technology that uses light with a wavelength of 13.5 nanometers to create extremely small features on computer chips. It's crucial for producing advanced semiconductors at 7nm, 5nm, and 3nm process nodes. EUV lithography enables the continuation of Moore's Law by allowing manufacturers to create transistors and other features that are smaller and more densely packed than ever before. The technology is essential for producing the most advanced processors used in smartphones, computers, and AI applications.",
            "confidence": 0.92,
            "processing_time": 1.243,
            "sources": [
                {
                    "title": "EUV Lithography: Principles and Applications",
                    "source": "IEEE Transactions on Semiconductor Manufacturing",
                    "date": "2024-01-15",
                    "relevance": 0.94,
                    "excerpt": "EUV lithography operates at 13.5 nm wavelength, enabling sub-10nm feature resolution essential for advanced node manufacturing..."
                },
                {
                    "title": "ASML EUV Technology Overview",
                    "source": "ASML Technical Report",
                    "date": "2024-02-20",
                    "relevance": 0.87,
                    "excerpt": "The EUV scanner represents a $200M+ investment per unit, with each system capable of processing 150+ wafers per hour..."
                }
            ]
        }
    }
    
    # Simple keyword matching for demo
    query_lower = query.lower()
    if "euv" in query_lower or "lithography" in query_lower:
        return sample_responses["euv lithography"]
    else:
        # Generic response
        return {
            "answer": f"Based on the available semiconductor knowledge base, here's what I can tell you about '{query}': This is a sophisticated query that would benefit from more specific documentation in our knowledge base. The semiconductor industry is constantly evolving, and this topic represents an important area of ongoing research and development. For the most current information, I recommend checking the latest industry publications and technical papers.",
            "confidence": 0.65,
            "processing_time": 0.876,
            "sources": [
                {
                    "title": "Semiconductor Industry Overview",
                    "source": "Industry Analysis Report",
                    "date": "2024-03-01",
                    "relevance": 0.72,
                    "excerpt": "The semiconductor industry continues to advance rapidly with new technologies and processes..."
                }
            ]
        }

def show_knowledge_base():
    """Show knowledge base browser"""
    st.header("📊 Knowledge Base Browser")
    st.markdown("Explore the documents and knowledge stored in the system.")
    
    # Sample data
    sample_docs = create_sample_data()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        source_filter = st.selectbox(
            "Filter by source:",
            ["All"] + list(set([doc['source'] for doc in sample_docs]))
        )
    with col2:
        topic_filter = st.selectbox(
            "Filter by topic:",
            ["All"] + list(set([topic for doc in sample_docs for topic in doc['topics']]))
        )
    with col3:
        date_filter = st.date_input("Filter by date (after):", value=None)
    
    # Document display
    filtered_docs = sample_docs
    if source_filter != "All":
        filtered_docs = [doc for doc in filtered_docs if doc['source'] == source_filter]
    if topic_filter != "All":
        filtered_docs = [doc for doc in filtered_docs if topic_filter in doc['topics']]
    
    st.write(f"**Showing {len(filtered_docs)} documents**")
    
    for i, doc in enumerate(filtered_docs):
        with st.expander(f"📄 {doc['title']}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(doc['content'])
            with col2:
                st.write(f"**Source:** {doc['source']}")
                st.write(f"**Date:** {doc['date']}")
                st.write(f"**Topics:** {', '.join(doc['topics'])}")
                if st.button(f"🔍 Query about this", key=f"query_doc_{i}"):
                    st.switch_page("🤖 RAG Query System")
    
    # Document upload interface
    st.divider()
    st.subheader("📤 Upload New Document")
    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf', 'docx'])
    if uploaded_file:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                time.sleep(2)
                st.success("Document processed and added to knowledge base!")

def show_crawling_interface():
    """Show web crawling interface"""
    st.header("🕷️ Web Crawling Interface")
    st.markdown("Manage automated data collection from semiconductor industry sources.")
    
    # Data sources configuration
    st.subheader("📂 Data Sources")
    
    sources = [
        {"name": "ArXiv Papers", "url": "arxiv.org", "status": "active", "last_crawl": "2024-07-27 14:30"},
        {"name": "IEEE Xplore", "url": "ieeexplore.ieee.org", "status": "active", "last_crawl": "2024-07-27 09:15"},
        {"name": "Semiconductor News", "url": "various news sites", "status": "active", "last_crawl": "2024-07-28 08:00"},
        {"name": "Patent Database", "url": "patents.google.com", "status": "inactive", "last_crawl": "2024-07-26 16:45"},
        {"name": "Industry Reports", "url": "various industry sites", "status": "active", "last_crawl": "2024-07-27 20:30"}
    ]
    
    for source in sources:
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"**{source['name']}**")
        with col2:
            st.write(source['url'])
        with col3:
            if source['status'] == 'active':
                st.success("Active")
            else:
                st.error("Inactive")
        with col4:
            st.write(source['last_crawl'])
    
    st.divider()
    
    # Crawling controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Manual Crawling")
        selected_sources = st.multiselect(
            "Select sources to crawl:",
            [source['name'] for source in sources]
        )
        
        if st.button("Start Crawling", type="primary"):
            if selected_sources:
                with st.spinner("Starting crawling process..."):
                    progress_bar = st.progress(0)
                    for i, source in enumerate(selected_sources):
                        st.write(f"Crawling {source}...")
                        time.sleep(1)
                        progress_bar.progress((i + 1) / len(selected_sources))
                    st.success("Crawling completed successfully!")
            else:
                st.warning("Please select at least one source to crawl.")
    
    with col2:
        st.subheader("⏰ Scheduled Crawling")
        st.write("Current schedule:")
        st.info("📅 Daily crawling at 2:00 AM UTC")
        st.info("🔄 Weekly deep crawling on Sundays")
        
        if st.button("Modify Schedule"):
            st.write("Schedule modification interface would go here...")
    
    # Crawling statistics
    st.subheader("📊 Crawling Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents Crawled Today", "23", "+15")
    with col2:
        st.metric("Average Processing Time", "2.3s", "-0.5s")
    with col3:
        st.metric("Success Rate", "94.2%", "+2.1%")

def show_system_monitor():
    """Show system monitoring interface"""
    st.header("🔧 System Monitor")
    st.markdown("Real-time monitoring of system health and performance.")
    
    # System status
    try:
        system_status = get_system_status()
        
        st.subheader("🏥 System Health")
        
        if 'overall_status' in system_status:
            overall_status = system_status['overall_status']
            if overall_status == 'healthy':
                st.success(f"✅ System Status: {overall_status.title()}")
            elif overall_status == 'warning':
                st.warning(f"⚠️ System Status: {overall_status.title()}")
            else:
                st.error(f"❌ System Status: {overall_status.title()}")
        
        # Component status
        components = ['database', 'filesystem', 'configuration', 'api_connectivity']
        cols = st.columns(len(components))
        
        for i, component in enumerate(components):
            with cols[i]:
                if component in system_status:
                    status_info = system_status[component]
                    if isinstance(status_info, dict) and 'status' in status_info:
                        status = status_info['status']
                        st.markdown(f"**{component.title()}**")
                        st.markdown(format_status_display(status), unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{component.title()}**")
                        st.info("Status unknown")
                else:
                    st.markdown(f"**{component.title()}**")
                    st.info("Not monitored")
    
    except Exception as e:
        st.error(f"Error fetching system status: {e}")
    
    st.divider()
    
    # Performance metrics
    st.subheader("📈 Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CPU and Memory usage (simulated)
        st.write("**Resource Usage**")
        cpu_usage = 23.5
        memory_usage = 45.2
        disk_usage = 15.8
        
        st.metric("CPU Usage", f"{cpu_usage}%")
        st.progress(cpu_usage / 100)
        
        st.metric("Memory Usage", f"{memory_usage}%")
        st.progress(memory_usage / 100)
        
        st.metric("Disk Usage", f"{disk_usage}%")
        st.progress(disk_usage / 100)
    
    with col2:
        # Response times (simulated)
        st.write("**Response Times**")
        times = pd.DataFrame({
            'Time': pd.date_range('2024-07-28 00:00', periods=24, freq='H'),
            'Response Time (ms)': [800 + i*10 + (i%3)*50 for i in range(24)]
        })
        
        fig = px.line(times, x='Time', y='Response Time (ms)', title='24-Hour Response Time Trend')
        st.plotly_chart(fig, use_container_width=True)
    
    # System logs
    st.subheader("📋 Recent System Logs")
    sample_logs = [
        {"timestamp": "2024-07-28 12:45:23", "level": "INFO", "message": "RAG query processed successfully"},
        {"timestamp": "2024-07-28 12:44:15", "level": "INFO", "message": "Document added to knowledge base"},
        {"timestamp": "2024-07-28 12:43:02", "level": "WARNING", "message": "API rate limit approaching"},
        {"timestamp": "2024-07-28 12:42:18", "level": "INFO", "message": "Scheduled crawling started"},
        {"timestamp": "2024-07-28 12:41:30", "level": "INFO", "message": "Health check completed"},
    ]
    
    log_df = pd.DataFrame(sample_logs)
    st.dataframe(log_df, use_container_width=True)

def show_analytics():
    """Show analytics and insights"""
    st.header("📈 Analytics & Insights")
    st.markdown("Advanced analytics and insights about system usage and knowledge base growth.")
    
    # Usage analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Query Analytics")
        
        # Top topics
        topics_data = {
            'Topic': ['EUV Lithography', '3nm Process', 'AI in Manufacturing', 'Yield Optimization', 'Memory Technologies'],
            'Queries': [45, 38, 32, 28, 22]
        }
        fig = px.bar(topics_data, x='Queries', y='Topic', orientation='h', title='Most Queried Topics')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Geographic Distribution")
        
        # Geographic data (simulated)
        geo_data = {
            'Country': ['United States', 'Taiwan', 'South Korea', 'Japan', 'Germany', 'China'],
            'Users': [156, 89, 67, 45, 34, 123]
        }
        fig = px.pie(geo_data, values='Users', names='Country', title='User Distribution by Country')
        st.plotly_chart(fig, use_container_width=True)
    
    # Knowledge base analytics
    st.subheader("📚 Knowledge Base Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Documents", "1,247", "+156 this month")
        st.metric("Unique Topics", "89", "+12 this month")
    
    with col2:
        st.metric("Average Document Length", "2,340 words", "+15% vs last month")
        st.metric("Citation Accuracy", "94.2%", "+1.3% improvement")
    
    with col3:
        st.metric("User Satisfaction", "4.6/5.0", "+0.2 vs last month")
        st.metric("Query Success Rate", "91.8%", "+2.1% improvement")
    
    # Trend analysis
    st.subheader("📈 Trend Analysis")
    
    # Create sample trend data
    dates = pd.date_range(start='2024-01-01', end='2024-07-28', freq='W')
    trends_data = pd.DataFrame({
        'Date': dates,
        'Documents Added': [20 + i*2 + (i%4)*5 for i in range(len(dates))],
        'Queries Processed': [150 + i*10 + (i%3)*20 for i in range(len(dates))],
        'User Engagement': [0.7 + (i%10)*0.02 for i in range(len(dates))]
    })
    
    tab1, tab2, tab3 = st.tabs(["📄 Document Growth", "🔍 Query Volume", "👥 User Engagement"])
    
    with tab1:
        fig = px.line(trends_data, x='Date', y='Documents Added', title='Weekly Document Addition Trend')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.line(trends_data, x='Date', y='Queries Processed', title='Weekly Query Volume Trend')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = px.line(trends_data, x='Date', y='User Engagement', title='User Engagement Score Trend')
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
