"""
Multi-Project Streamlit Hub
One app hosting multiple projects
"""

import streamlit as st

def main():
    st.set_page_config(
        page_title="My Project Hub",
        page_icon="🚀",
        layout="wide"
    )
    
    # Sidebar for project selection
    st.sidebar.title("🚀 Project Hub")
    
    projects = {
        "🔬 Semiconductor Learning": "semiconductor_project",
        "📊 Data Analytics": "analytics_project", 
        "🤖 AI Assistant": "ai_project",
        "🎯 Portfolio Tracker": "portfolio_project"
    }
    
    selected_project = st.sidebar.selectbox(
        "Select Project:", 
        list(projects.keys())
    )
    
    project_id = projects[selected_project]
    
    # Load the selected project
    if project_id == "semiconductor_project":
        load_semiconductor_app()
    elif project_id == "analytics_project":
        load_analytics_app()
    elif project_id == "ai_project":
        load_ai_app()
    elif project_id == "portfolio_project":
        load_portfolio_app()

def load_semiconductor_app():
    # Your existing semiconductor app code here
    exec(open('streamlit_demo_simple.py').read())

def load_analytics_app():
    st.title("📊 Data Analytics Project")
    st.write("Your analytics project here...")

def load_ai_app():
    st.title("🤖 AI Assistant Project") 
    st.write("Your AI project here...")

def load_portfolio_app():
    st.title("🎯 Portfolio Tracker")
    st.write("Your portfolio project here...")

if __name__ == "__main__":
    main()
