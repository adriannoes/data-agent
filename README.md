# Data Analyst - AI Agent

An agentic conversational data analysis platform powered by LangGraph. Analyze CSV data through natural language conversations with real-time preview updates.

## Overview

Full-stack application that combines an intelligent agent architecture with a modern web interface. The system uses LangGraph to orchestrate a multi-step workflow that understands user intent, processes data, and generates insights—all while streaming updates to the frontend in real-time.

## Agent Architecture

The core of the system is a **LangGraph state machine** that processes user queries through three sequential nodes:

1. **Understand Intent** - Uses OpenAI GPT-4o to analyze user messages and extract analysis requirements
2. **Process Data** - Executes data operations (loading, filtering, summarizing) using Pandas tools
3. **Generate Response** - Synthesizes results into natural language responses

The agent maintains conversation context and streams status updates via Server-Sent Events (SSE) for real-time UI feedback.

## Technology Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **SSE (Server-Sent Events)** - Real-time streaming updates

### Backend
- **FastAPI** - REST API framework
- **LangGraph** - Agent orchestration and state management
- **LangChain** - LLM integration framework
- **OpenAI GPT-3.5-turbo** - Natural language understanding and generation
- **Pandas** - Data analysis and manipulation
- **SSE-Starlette** - Server-Sent Events streaming

## Project Structure

```
ai-datalab/
├── backend/
│   ├── agent/
│   │   ├── graph.py      # LangGraph state machine definition
│   │   └── nodes.py      # Agent nodes (understand, process, respond)
│   ├── tools/
│   │   └── data_analysis.py  # Pandas-based data operations
│   ├── data/             # CSV files for analysis
│   └── main.py           # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks (useSSE)
│   │   └── App.tsx       # Main application
│   ├── package.json      # Frontend dependencies
│   └── vite.config.ts    # Vite configuration
└── ...
```

## Setup

### Prerequisites
- Node.js 18+
- Python 3.8+
- OpenAI API key

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5175`

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
python main.py
```

Backend runs on `http://localhost:8000`

## Usage

1. Start the backend server
2. Start the frontend dev server
3. Place CSV files in `backend/data/`
4. Chat with the agent to analyze your data
5. View real-time analysis results in the preview panel

## API Endpoints

- `POST /api/chat` - Process chat messages through the agent
- `GET /api/stream/{session_id}` - SSE stream for real-time updates
- `GET /api/health` - Health check

## Build

```bash
cd frontend
npm run build
```

