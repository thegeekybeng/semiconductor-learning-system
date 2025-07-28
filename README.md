# 🔬 Semiconductor Manufacturing Self-Learning Module

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

A comprehensive AI-powered system that continuously learns about semiconductor manufacturing processes, technological advancements, and AI implementations in the industry.

## 🚀 **Live Demo**

**Try the live demo:** [Semiconductor Learning System](https://your-app-name.streamlit.app)

## Features

- **Automated Web Crawling**: Uses crawl4ai to continuously gather information from semiconductor industry sources
- **RAG System**: Advanced Retrieval Augmented Generation for intelligent information processing
- **Historical Analysis**: Tracks and analyzes 30+ years of semiconductor technological evolution
- **Self-Training**: Automatically processes new data and updates knowledge base
- **Scheduled Updates**: Runs on configurable schedules to stay current with industry developments
- **Multi-Source Integration**: Aggregates data from research papers, industry reports, news, and technical documentation

## Architecture

```
semiconductor_learning/
├── core/                   # Core system components
├── crawlers/              # Web crawling modules
├── rag/                   # RAG system implementation
├── models/                # AI models and training
├── data/                  # Data storage and management
├── schedulers/            # Automated task scheduling
├── api/                   # REST API endpoints
├── config/                # Configuration files
└── scripts/               # Utility scripts
```

## Quick Start

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Initialize Database**:

   ```bash
   python scripts/init_db.py
   ```

4. **Start the System**:
   ```bash
   python main.py
   ```

## Configuration

The system uses environment variables for configuration. Key settings include:

- `OPENAI_API_KEY`: For LLM integration
- `CHROMA_DB_PATH`: Vector database storage path
- `CRAWL_SCHEDULE`: Schedule for automated crawling
- `MAX_CRAWL_DEPTH`: Maximum crawling depth
- `UPDATE_FREQUENCY`: Model update frequency

## Usage

### Manual Data Collection

```bash
python scripts/crawl_sources.py --source semiconductor_news
```

### Query the Knowledge Base

```bash
python scripts/query.py "How has EUV lithography evolved in the last decade?"
```

### Start Automated Learning

```bash
python scripts/start_scheduler.py
```

## Contributing

This is an autonomous learning system designed to self-improve and expand its knowledge base continuously.

## License

MIT License
