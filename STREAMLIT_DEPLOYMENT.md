# Streamlit Cloud Deployment Instructions

## Quick Setup for Streamlit Cloud

1. **Main File**: Use `streamlit_demo.py` (NOT `demo_launcher.py`)
2. **Python Version**: 3.11+
3. **Dependencies**: All listed in `requirements.txt`

# Streamlit Cloud Deployment Instructions

## 🚨 **IMPORTANT: Use the Simplified Demo**

Due to ChromaDB compatibility issues with Python 3.13 on Streamlit Cloud, use the simplified version:

1. **Main File**: Use `streamlit_demo_simple.py` (NOT `streamlit_demo.py` or `demo_launcher.py`)
2. **Python Version**: 3.11+
3. **Dependencies**: Reduced set - works without ChromaDB

## Environment Variables to Set in Streamlit Cloud:

```
OPENAI_API_KEY=your-api-key-here
```

## Deployment Steps:

1. Fork/clone this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository: `thegeekybeng/semiconductor-learning-system`
5. **Main file path**: `streamlit_demo_simple.py`

## Deployment Steps:

1. Fork/clone this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository: `thegeekybeng/semiconductor-learning-system`
5. **Main file path**: `streamlit_demo.py`
6. Click "Advanced settings"
7. Add environment variable: `OPENAI_API_KEY=your-key`
8. Click "Deploy"

## What's Different in the Simplified Version:

✅ **Includes:**

- Full Streamlit UI with all 6 pages
- Sample semiconductor knowledge base
- RAG query simulation
- OpenAI GPT-4 integration (when API key provided)
- Interactive charts and analytics
- System monitoring dashboard

❌ **Excluded (due to compatibility):**

- ChromaDB vector database (uses in-memory sample data)
- Web crawling functionality (shows simulated data)
- File-based persistence (uses session state)

## Important Notes:

- **DO NOT** use `demo_launcher.py` on Streamlit Cloud
- Use `streamlit_demo_simple.py` as your main file
- Set the OpenAI API key in the Streamlit Cloud secrets/environment variables
- The app will be available at: `https://your-app-name.streamlit.app`

## Troubleshooting:

If you see "Port 8501 is already in use":

- Make sure you're using `streamlit_demo_simple.py` as the main file
- Check that `demo_launcher.py` is not being used
- Streamlit Cloud manages ports automatically

If you see ChromaDB errors:

- Make sure you're using `streamlit_demo_simple.py` (not `streamlit_demo.py`)
- The simplified version doesn't require ChromaDB

## Local Development:

For local testing: `python demo_launcher.py`
For Streamlit Cloud: Use `streamlit_demo_simple.py` directly

## Important Notes:

- **DO NOT** use `demo_launcher.py` on Streamlit Cloud
- Use `streamlit_demo.py` as your main file
- Set the OpenAI API key in the Streamlit Cloud secrets/environment variables
- The app will be available at: `https://your-app-name.streamlit.app`

## Troubleshooting:

If you see "Port 8501 is already in use":

- Make sure you're using `streamlit_demo.py` as the main file
- Check that `demo_launcher.py` is not being used
- Streamlit Cloud manages ports automatically

## Local Development:

For local testing, use: `python demo_launcher.py`
For Streamlit Cloud: Use `streamlit_demo.py` directly
