# Streamlit Cloud Deployment Instructions

## Quick Setup for Streamlit Cloud

1. **Main File**: Use `streamlit_demo.py` (NOT `demo_launcher.py`)
2. **Python Version**: 3.11+
3. **Dependencies**: All listed in `requirements.txt`

## Environment Variables to Set in Streamlit Cloud:

```
OPENAI_API_KEY=your-api-key-here
```

## Deployment Steps:

1. Fork/clone this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository: `thegeekybeng/semiconductor-learning-system`
5. **Main file path**: `streamlit_demo.py`
6. Click "Advanced settings"
7. Add environment variable: `OPENAI_API_KEY=your-key`
8. Click "Deploy"

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
