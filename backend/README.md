# Socrates Backend - AI-Powered Study Assistant

Socrates is an AI-powered study assistant that turns documents into structured, adaptive learning experiences. The backend extracts Knowledge Units (facts and skills) from documents, generates adaptive questions using LLMs, assesses user answers, and tracks learning mastery over time.

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

## How It Works

### Learning Workflow

The backend implements a complete learning workflow that operates as a closed learning loop:

1. **Document Processing** → A PDF document is uploaded and parsed into text
2. **Knowledge Extraction** → Extract Knowledge Units from the text:
   - **Fact Knowledge**: Answers are grounded in explicit claims from the document
   - **Skill Knowledge**: Answers require applying the document's knowledge to new or practical situations
3. **Learning Plan Creation** → Select and organize knowledge units to master
4. **Study Session** → Generate questions whose difficulty adapts to the mastery of each selected Knowledge Unit
5. **Answer Evaluation** → Assess correctness of learner responses automatically
6. **Mastery Tracking** → Update knowledge unit mastery based on performance and repeat from step 4

All steps except mastery selection, mastery updates, and session scheduling (steps 3, 6, and repeat logic) are powered by LLMs.

The system uses Clean Architecture with clear separation between domain logic, application use cases, and infrastructure adapters. All LLM interactions are powered by OpenAI's GPT-4o and fully traced using Opik for observability.

### Observability and Evaluation

All LLM-related processes are fully traced using Opik. Traces are grouped into threads, where each thread represents a complete interaction starting from document ingestion.

The system incorporates user feedback and automated evaluation across multiple dimensions:

#### Question Coverage and Quality
- Coverage: Does the question adequately address the input overall?
- Completeness: Does the question sufficiently test the key aspects of the concept?
- Redundancy: Is there unnecessary repetition?
- Answer feasibility: Can the question be answered using plain text input?

#### Knowledge Unit Generation Quality
- Relevance: How useful the unit is for learning the input material
- Grounding: Whether claims are supported by the source text
- Diversity: Whether units cover distinct aspects of the input
- Complexity: Whether some units require synthesis across multiple parts of the document
- Redundancy: Degree of unnecessary repetition

#### Answer Assessment Quality
- Correctness: Does the user's answer accurately address the question and align with the expected solution?
- Leniency/strictness calibration: Is the judgment appropriately strict or lenient given the question's difficulty and intent?
- Explanation quality: Is the explanation clear and helpful for learning?
- Pedagogical usefulness: Would this assessment help the user improve their understanding?

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