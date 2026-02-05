# Socrates - AI-Powered Study Assistant

An AI-powered study assistant that extracts knowledge from documents, generates adaptive questions, and tracks learning progress using mastery-based learning.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js
- OpenAI API key
- Gemini API key

### Setup

1. **Backend Setup**
   ```bash
   cd backend
   pip install -e .

   # Create .env file
   cat > .env << EOF
   OPENAI_API_KEY=your_openai_api_key_here
   OPIK_PROJECT_NAME=socrates
   EOF
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install

   # Set GEMINI_API_KEY in .env.local
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env.local
   ```

### Running the Application

1. **Start the Backend** (in `backend/` directory):
   ```bash
   python main.py
   ```
   API will be available at `http://localhost:8000`

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