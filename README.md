# Bengali RAG System

A production-level Retrieval Augmented Generation (RAG) system that handles both English and Bengali queries. The system uses a PDF document corpus as its knowledge base and maintains both short-term and long-term memory for better context handling.

## Features

- Bilingual query support (English and Bengali)
- PDF document processing and chunking
- Vector storage using SQLite
- REST API for easy integration
- Long-short term memory management
- RAG evaluation metrics
- Uses Ollama for LLM operations

## Project Structure

```
.
├── src/
│   ├── api/             # FastAPI related code
│   ├── core/            # Core RAG implementation
│   ├── database/        # Database models and operations
│   ├── embeddings/      # Embedding models and utils
│   └── utils/           # Helper functions
├── data/               # Store PDF documents
├── tests/             # Unit and integration tests
├── .env               # Environment variables
└── requirements.txt   # Project dependencies
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Ollama and run the model:
```bash
# Download and run Ollama with a suitable model (e.g., llama2)
ollama pull llama2
ollama run llama2
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
uvicorn src.api.main:app --reload
```

## API Usage

The API provides endpoints for:
- Query processing (POST /api/query)
- Document ingestion (POST /api/ingest)
- System evaluation (GET /api/evaluate)

Example query:
```bash
curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?", "chat_history": []}'
```

## Testing

Run tests using:
```bash
pytest tests/
```

## License

MIT License
