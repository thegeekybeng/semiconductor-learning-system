"""
AI Assistant App Module  
For the Streamlit Hub Architecture
"""

import streamlit as st

def main():
    """AI Assistant application"""
    st.title("🤖 AI Assistant")
    st.markdown("*Multi-purpose AI chat assistant*")
    
    # Simple chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add assistant response
        with st.chat_message("assistant"):
            response = f"🤖 Thanks for your question: '{prompt}'. This is a demo response. In the full version, this would connect to OpenAI or another AI service."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar features
    with st.sidebar:
        st.subheader("🛠️ AI Features")
        
        if st.button("💭 Brainstorming Mode"):
            st.info("Brainstorming mode activated!")
        
        if st.button("📝 Writing Assistant"):
            st.info("Writing assistant ready!")
        
        if st.button("🔍 Research Helper"):
            st.info("Research mode enabled!")
        
        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()
