# Socrates Backend - AI-Powered Study Assistant

An AI-powered study assistant that extracts knowledge from documents, generates adaptive questions, and tracks learning progress using mastery-based learning.

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. Install dependencies (using Poetry):
```bash
# If you don't have Poetry installed, follow https://python-poetry.org/docs/#installation
poetry install
```

2. Set up environment variables:

Create a file named `.env` in the `backend` directory and add the required variables. Wrap values in double quotes, for example:

```text
OPENAI_API_KEY="your_openai_api_key_here"
OPIK_PROJECT_NAME="socrates"
```

### Running the Application

Start the FastAPI server:

```bash
# from the backend folder (use Poetry to run in the project's venv)
poetry run python main.py
```

The API will be available at `http://localhost:8000`

- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### Opik Configuration (OPTIONAL)

If you want to configure Opik for tracking:

```bash
# Get the environment activation command
poetry env activate

# Run the returned source command (e.g., source /path/to/venv/bin/activate)
# Copy and run the path returned by the previous command

# Configure Opik
opik configure
```

### Running Tests

Run the full test suite (via Poetry):

```bash
poetry run pytest
```

Run with coverage (via Poetry):

```bash
poetry run pytest --cov=. --cov-report=term-missing
```

## Architecture

The backend follows Clean Architecture principles:

- **Domain**: Core business entities and interfaces
- **Application**: Use cases and application services
- **Infrastructure**: External integrations (OpenAI, repositories)

## Key Features

- Document ingestion and knowledge extraction
- AI-generated questions from learning materials
- Adaptive learning plans with mastery tracking
- RESTful API for frontend integration

## Configuration

Main settings can be configured via `config.yaml` or environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_COMPLETION_MODEL`: Model for text completion (default: gpt-4o)
- `STUDY_SESSION_MAX_QUESTIONS`: Max questions per session (default: 10)