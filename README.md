# Socrates - AI-Powered Study Assistant

An AI-powered study assistant that extracts knowledge from documents, generates adaptive questions, and tracks learning progress using mastery-based learning.

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

## Project Structure

- **[Backend](./backend/README.md)** - FastAPI server with Clean Architecture
- **[Frontend](./frontend/README.md)** - AI Studio app interface

## Features

- Document ingestion and knowledge extraction
- AI-generated adaptive questions
- Mastery-based learning progress tracking
- Interactive study sessions