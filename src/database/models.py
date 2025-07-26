from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import os
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    doc_metadata = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(String)
    embedding = Column(String)  # Store embeddings as serialized string
    document = relationship("Document", back_populates="chunks")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(String)
    system_response = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database URL
DATABASE_URL = "sqlite+aiosqlite:///./rag_system.db"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Initialize the database with all tables"""
    try:
        async with engine.begin() as conn:
            # Drop all tables if they exist
            await conn.run_sync(Base.metadata.drop_all)
            # Create all tables fresh
            await conn.run_sync(Base.metadata.create_all)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
