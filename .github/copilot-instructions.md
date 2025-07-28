<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Semiconductor Manufacturing Self-Learning Module - Copilot Instructions

This project is a comprehensive AI-powered system that continuously learns about semiconductor manufacturing processes, technological advancements, and AI implementations in the industry.

## Project Overview

- **Primary Purpose**: Autonomous learning system for semiconductor manufacturing knowledge
- **Key Technologies**: RAG (Retrieval Augmented Generation), crawl4ai, vector databases, automated scheduling
- **Architecture**: Modular Python application with async processing capabilities

## Key Components

### Core System (`core/`)
- `config.py`: Centralized configuration management using Pydantic
- `database.py`: ChromaDB integration for vector storage and SQLite for metadata
- `system_monitor.py`: Health monitoring and performance tracking

### Data Collection (`crawlers/`)
- `crawler_manager.py`: Manages web crawling using crawl4ai
- Focuses on semiconductor industry sources (ArXiv, IEEE, news, patents, industry reports)
- Configurable crawling schedules and source management

### RAG System (`rag/`)
- `query_engine.py`: Advanced query processing with OpenAI integration
- Historical timeline analysis capabilities
- Context-aware response generation

### Model Training (`models/`)
- `training_manager.py`: Continuous learning and model updates
- Incremental training capabilities
- Performance monitoring and evaluation

### Automation (`schedulers/`)
- `main_scheduler.py`: APScheduler-based automation
- Configurable cron-like scheduling for all tasks
- Health checks and maintenance automation

### API Interface (`api/`)
- `server.py`: FastAPI-based REST API
- Comprehensive endpoints for querying, crawling, training, and monitoring

## Coding Guidelines

1. **Error Handling**: Always use try-catch blocks with proper logging
2. **Async/Await**: Use async programming for I/O operations
3. **Configuration**: Use the centralized config system for all settings
4. **Logging**: Use structured logging with appropriate levels
5. **Type Hints**: Include comprehensive type annotations
6. **Documentation**: Maintain detailed docstrings for all functions

## Domain Knowledge

When working with this codebase, keep in mind:

- **Semiconductor Manufacturing**: 30+ years of technological evolution
- **Key Technologies**: EUV lithography, AI chip design, process nodes, memory technologies
- **Industry Sources**: Focus on authoritative sources like IEEE, ArXiv, industry leaders
- **Historical Context**: Track technological milestones and evolution patterns

## Development Patterns

- Use dependency injection for testability
- Implement graceful degradation when optional libraries are unavailable
- Follow the async/await pattern for all I/O operations
- Use Pydantic models for data validation
- Implement comprehensive error logging and monitoring

## Special Considerations

- The system should be self-learning and autonomous
- Handle missing dependencies gracefully with fallback options
- Prioritize data quality and source reliability
- Maintain historical accuracy and technical precision
- Ensure scalability for large datasets and continuous operation
