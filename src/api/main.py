from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from src.database.models import get_session, Document, DocumentChunk, init_db
from src.core.rag import RAGSystem
from src.core.processors import DocumentProcessor, EmbeddingManager

app = FastAPI(title="Bengali RAG System API")

@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup"""
    await init_db()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    chat_history: Optional[List[Dict[str, str]]] = None

class QueryResponse(BaseModel):
    answer: str
    evaluation: Optional[Dict[str, float]] = None
    source_contexts: Optional[List[Dict[str, Any]]] = None
    language: str = "en"  # "en" for English, "bn" for Bengali

@app.post("/api/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    session: AsyncSession = Depends(get_session)
):
    """Process a user query in Bengali or English and return the response with evaluation metrics."""
    try:
        # Initialize RAG system
        rag_system = RAGSystem(session)
        
        # Detect language and validate query
        is_bengali = any('\u0980' <= c <= '\u09FF' for c in request.query)
        if len(request.query.strip()) < 3:
            raise HTTPException(
                status_code=400, 
                detail="Query too short. Please provide a more detailed question."
            )
            
        # Process query and get response
        response = await rag_system.process_query(request.query, request.chat_history)
        
        # Get relevant chunks for context and evaluation
        relevant_chunks = await rag_system._get_relevant_chunks(
            request.query,
            n_results=5 if is_bengali else 3  # More context for Bengali queries
        )
        
        # Evaluate response quality
        evaluation = await rag_system.evaluate_response(
            request.query,
            response,
            relevant_chunks
        )
        
        # Get source context for response
        source_contexts = []
        for chunk in relevant_chunks:
            doc_id = chunk.document_id
            stmt = select(Document).where(Document.id == doc_id)
            result = await session.execute(stmt)
            document = result.scalar_one_or_none()
            if document:
                source_contexts.append({
                    "document": document.doc_metadata,
                    "relevance_score": evaluation.get("relevance", 0)
                })
        
        return QueryResponse(
            answer=response,
            evaluation=evaluation,
            source_contexts=source_contexts,
            language="bn" if is_bengali else "en"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()

@app.post("/api/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """Ingest a PDF document into the system."""
    try:
        # Save uploaded file
        file_location = f"data/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        
        # Process document
        doc_processor = DocumentProcessor()
        embedding_manager = EmbeddingManager()
        
        # Process the PDF into chunks
        chunks = await doc_processor.process_pdf(file_location)
        
        # Create document entry
        document = Document(
            content=file_location,
            doc_metadata=json.dumps({"filename": file.filename, "type": "pdf"})
        )
        session.add(document)
        await session.flush()  # Get the document ID
        
        # Process and store chunks with embeddings
        for chunk in chunks:
            # Generate embedding
            embedding = embedding_manager.get_embeddings([chunk['content']])[0]
            embedding_str = embedding_manager.serialize_embedding(embedding)
            
            # Create chunk entry
            doc_chunk = DocumentChunk(
                document_id=document.id,
                content=chunk['content'],
                embedding=embedding_str
            )
            session.add(doc_chunk)
        
        await session.commit()
        
        return {
            "message": "Document ingested successfully",
            "details": {
                "document_id": document.id,
                "chunks_processed": len(chunks),
                "filename": file.filename
            }
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()

@app.get("/api/evaluate")
async def get_system_metrics(session: AsyncSession = Depends(get_session)):
    """Get system-wide evaluation metrics."""
    try:
        # Implement system-wide evaluation logic here
        # This could include:
        # - Average response time
        # - Average evaluation scores
        # - Number of successful queries
        # - etc.
        return {
            "message": "System evaluation metrics retrieved successfully",
            "metrics": {
                "status": "operational"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
