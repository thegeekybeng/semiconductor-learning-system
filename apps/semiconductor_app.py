"""
Semiconductor Learning App Module
For the Streamlit Hub Architecture
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import the main demo
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

def main():
    """Main function for the semiconductor app"""
    st.title("🔬 Semiconductor Learning System")
    st.markdown("*Running within the Streamlit Hub*")
    
    # Import and run the main semiconductor demo
    try:
        # Import the main app functions from streamlit_demo_simple
        from streamlit_demo_simple import (
            show_dashboard, show_rag_query, show_knowledge_base,
            show_web_crawling, show_system_monitor, show_analytics,
            openai_client
        )
        
        # Mini navigation for semiconductor app
        tabs = st.tabs(["🏠 Dashboard", "🤖 RAG Query", "📚 Knowledge", "📊 Monitor", "📈 Analytics"])
        
        with tabs[0]:
            show_dashboard()
        with tabs[1]:
            show_rag_query()
        with tabs[2]:
            show_knowledge_base()
        with tabs[3]:
            show_system_monitor()
        with tabs[4]:
            show_analytics()
            
    except ImportError as e:
        st.error(f"Could not import semiconductor demo: {e}")
        st.info("Make sure streamlit_demo_simple.py is in the same directory")
        
        # Fallback simple version
        st.subheader("🔬 Semiconductor Knowledge Demo")
        
        query = st.text_input("Ask about semiconductors:")
        if query:
            st.write("🤖 This is a simplified version. Full features available in standalone mode.")
            st.info(f"You asked: {query}")
            
            # Sample response
            st.markdown("""
            **Sample Response:** Semiconductor technology continues to evolve rapidly with 
            advances in EUV lithography, 3D NAND memory, and AI-driven chip design. The industry 
            focuses on smaller process nodes, improved power efficiency, and novel materials.
            """)

if __name__ == "__main__":
    main()
