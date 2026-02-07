# Socrates - AI-Powered Study Assistant

Socrates is an AI-powered study assistant that turns documents into structured, adaptive learning experiences. It uses LLMs to extract key facts and skills, generate personalized questions, assess answers, and track mastery over time, helping learners actually learn, not just read.

## Quick Start

### Prerequisites

- Python 3.11+ with Poetry
- Node.js
- OpenAI API key
- Gemini API key

### Setup

1. **Backend Setup**
   ```bash
   cd backend
   # If you don't have Poetry installed, follow https://python-poetry.org/docs/#installation
   poetry install
   ```

   Create a `.env` file in the `backend` directory with:
   ```text
   OPENAI_API_KEY="your_openai_api_key_here"
   OPIK_PROJECT_NAME="socrates"
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

   Create a `.env.local` file in the `frontend` directory with:
   ```text
   GEMINI_API_KEY=your_gemini_api_key_here
   # BACKEND_HOST=http://localhost:8000  # Optional if backend runs elsewhere
   ```

### Running the Application

1. **Start the Backend** (in `backend/` directory):
   ```bash
   poetry run python main.py
   ```

2. **Start the Frontend** (in `frontend/` directory):
   ```bash
   npm run dev
   ```

## How It Works

Socrates operates as a closed learning loop:

1. Upload a PDF document
2. Extract Knowledge Units (facts and skills) from the text
3. Generate adaptive questions based on current mastery levels
4. Assess user answers automatically
5. Update mastery levels and repeat

### System Architecture

- **React-based frontend** for user interaction
- **Python FastAPI backend** with Clean Architecture
- **OpenAI GPT-4o** for LLM processing
- **Opik** for full observability and tracing

## Project Structure

- **[Backend](./backend/README.md)** - FastAPI server with Clean Architecture
- **[Frontend](./frontend/README.md)** - AI Studio app interface

## Features

- Document ingestion and knowledge extraction
- AI-generated adaptive questions
- Mastery-based learning progress tracking
- Interactive study sessions