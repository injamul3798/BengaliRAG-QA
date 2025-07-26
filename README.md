# Bengali RAG System

A production-level Retrieval Augmented Generation (RAG) system that handles both English and Bengali queries. The system uses a PDF document corpus as its knowledge base and maintains both short-term and long-term memory for better context handling.
 
[bb01fbfe-4440-4daf-b720-616b9ab3f790.webm](https://github.com/user-attachments/assets/af03dd3b-9d1c-4b3f-82a4-dea0f6b74f67)

 

## Features

- Bilingual support (Bengali and English)
- Intelligent document chunking and retrieval
- TF-IDF based response generation
- SQLite vector storage
- FastAPI REST endpoints

## Quick Start

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the API server:
```bash
uvicorn src.api.main:app --reload
```

## API Usage

1. Upload document:
```bash
curl -X POST "http://localhost:8000/api/ingest" -F "file=@data/HSC26-Bangla1st-Paper.pdf"
```

2. Query the system:
```bash
curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?",
       "chat_history": []
     }'
```

## Sample Questions

- Q: অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?
  - A: শুম্ভুনাথ
- Q: কাকে অনুপমের ভাগ্য দেবতা বলে উল্লেখ করা হয়েছে?
  - A: মামাকে
- Q: বিয়ের সময় কল্যাণীর প্রকৃত বয়স কত ছিল?
  - A: ১৫ বছর

## Project Structure

```
.
├── src/
│   ├── api/        # FastAPI endpoints
│   ├── core/       # RAG implementation
│   ├── database/   # SQLite models
│   └── utils/      # Helper functions
├── data/           # PDF documents
└── tests/          # Test cases
```
