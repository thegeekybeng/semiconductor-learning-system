"""
🚀 THE ULTIMATE STREAMLIT HUB
One App to Rule All Your Projects

Modular architecture for hosting multiple Streamlit apps in one deployment
"""

import streamlit as st
import importlib.util
from pathlib import Path
import sys
from typing import Dict, Any
import traceback

# Configure the main hub
st.set_page_config(
    page_title="🚀 My Project Universe",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AppManager:
    """Manages multiple Streamlit applications"""
    
    def __init__(self):
        self.apps = {}
        self.register_apps()
    
    def register_apps(self):
        """Register all available apps"""
        self.apps = {
            "🏠 Hub Home": {
                "module": None,
                "description": "Welcome to your project universe",
                "status": "active",
                "category": "core"
            },
            "🔬 Semiconductor Learning": {
                "module": "semiconductor_app",
                "description": "AI-powered semiconductor knowledge system",
                "status": "active", 
                "category": "ai"
            },
            "📊 Data Analytics": {
                "module": "analytics_app",
                "description": "Advanced data analysis and visualization",
                "status": "development",
                "category": "analytics"
            },
            "🤖 AI Assistant": {
                "module": "ai_assistant_app", 
                "description": "Multi-purpose AI chat assistant",
                "status": "active",
                "category": "ai"
            },
            "💰 Portfolio Tracker": {
                "module": "portfolio_app",
                "description": "Investment portfolio management",
                "status": "planning",
                "category": "finance"
            },
            "🎮 Game Engine": {
                "module": "game_app",
                "description": "Interactive game development tools",
                "status": "experimental",
                "category": "entertainment"
            }
        }
    
    def load_app(self, app_name: str):
        """Dynamically load and execute an app"""
        app_config = self.apps.get(app_name)
        
        if not app_config or not app_config["module"]:
            self.show_home()
            return
            
        try:
            # Try to import the app module
            module_name = app_config["module"]
            
            # Check if module file exists
            module_path = Path(f"apps/{module_name}.py")
            if module_path.exists():
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Execute the main function if it exists
                if hasattr(module, 'main'):
                    module.main()
                elif hasattr(module, 'run'):
                    module.run()
                else:
                    st.error(f"App {app_name} doesn't have a main() or run() function")
            else:
                self.show_app_placeholder(app_name, app_config)
                
        except Exception as e:
            st.error(f"Error loading app {app_name}: {str(e)}")
            with st.expander("🐛 Debug Info"):
                st.code(traceback.format_exc())
    
    def show_home(self):
        """Show the hub home page"""
        st.title("🚀 Welcome to Your Project Universe")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🎯 Your Digital Workshop
            
            This is your centralized hub for all Streamlit projects. Each app runs 
            independently but shares the same deployment, saving you hosting costs 
            and simplifying management.
            
            **🌟 Benefits:**
            - ✅ One deployment, multiple apps
            - ✅ Shared resources and styling  
            - ✅ Easy navigation between projects
            - ✅ Unified user experience
            """)
            
            # App categories
            categories = {}
            for app_name, config in self.apps.items():
                if app_name == "🏠 Hub Home":
                    continue
                cat = config["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append((app_name, config))
            
            for category, apps in categories.items():
                st.subheader(f"📁 {category.title()} Apps")
                
                for app_name, config in apps:
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    
                    with col_a:
                        st.write(f"**{app_name}**")
                        st.caption(config["description"])
                    
                    with col_b:
                        status_color = {
                            "active": "🟢",
                            "development": "🟡", 
                            "planning": "🔵",
                            "experimental": "🟠"
                        }
                        st.write(f"{status_color.get(config['status'], '⚪')} {config['status']}")
                    
                    with col_c:
                        if st.button("Launch", key=f"launch_{app_name}"):
                            st.session_state.selected_app = app_name
                            st.rerun()
        
        with col2:
            # Quick stats
            st.subheader("📊 Hub Stats")
            total_apps = len(self.apps) - 1  # Exclude home
            active_apps = len([a for a in self.apps.values() if a["status"] == "active"])
            
            st.metric("Total Apps", total_apps)
            st.metric("Active Apps", active_apps)
            st.metric("Categories", len(categories))
            
            # Quick actions
            st.subheader("⚡ Quick Actions")
            if st.button("🎯 Random App", help="Try a random active app"):
                active_app_names = [name for name, config in self.apps.items() 
                                  if config["status"] == "active" and name != "🏠 Hub Home"]
                if active_app_names:
                    import random
                    random_app = random.choice(active_app_names)
                    st.session_state.selected_app = random_app
                    st.rerun()
    
    def show_app_placeholder(self, app_name: str, config: Dict[str, Any]):
        """Show placeholder for apps under development"""
        st.title(f"{app_name}")
        
        status_messages = {
            "development": "🚧 This app is currently under development",
            "planning": "📋 This app is in the planning phase", 
            "experimental": "🔬 This app is experimental"
        }
        
        st.info(status_messages.get(config["status"], "This app is not ready yet"))
        st.write(f"**Description:** {config['description']}")
        
        if config["status"] == "development":
            st.markdown("""
            ### 🛠️ Development Status
            - [ ] Core functionality
            - [ ] UI/UX design
            - [ ] Testing
            - [ ] Documentation
            """)
        
        if st.button("🏠 Back to Hub"):
            st.session_state.selected_app = "🏠 Hub Home"
            st.rerun()

def main():
    """Main hub application"""
    
    # Initialize app manager
    if 'app_manager' not in st.session_state:
        st.session_state.app_manager = AppManager()
    
    app_manager = st.session_state.app_manager
    
    # Sidebar navigation
    st.sidebar.title("🚀 Project Universe")
    st.sidebar.markdown("---")
    
    # App selector
    selected_app = st.sidebar.selectbox(
        "🎯 Select Application:",
        list(app_manager.apps.keys()),
        index=0 if 'selected_app' not in st.session_state else 
              list(app_manager.apps.keys()).index(st.session_state.get('selected_app', "🏠 Hub Home"))
    )
    
    # Update session state
    st.session_state.selected_app = selected_app
    
    # App info in sidebar
    if selected_app in app_manager.apps:
        config = app_manager.apps[selected_app]
        st.sidebar.markdown(f"**Status:** {config['status']}")
        st.sidebar.markdown(f"**Category:** {config['category']}")
        
        if config.get('description'):
            st.sidebar.caption(config['description'])
    
    st.sidebar.markdown("---")
    
    # Hub controls
    st.sidebar.subheader("🛠️ Hub Controls")
    
    if st.sidebar.button("🏠 Hub Home"):
        st.session_state.selected_app = "🏠 Hub Home"
        st.rerun()
        
    if st.sidebar.button("🔄 Refresh Apps"):
        app_manager.register_apps()
        st.rerun()
    
    # Theme toggle
    if st.sidebar.button("🎨 Toggle Theme"):
        # This would require additional theme management
        st.sidebar.info("Theme switching coming soon!")
    
    # Load the selected app
    app_manager.load_app(selected_app)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("🚀 Powered by Streamlit Hub Architecture")

if __name__ == "__main__":
    main()
