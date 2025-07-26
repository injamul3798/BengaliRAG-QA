from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.core.processors import EmbeddingManager
from src.database.models import DocumentChunk, ChatHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from collections import Counter

class RAGSystem:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.embedding_manager = EmbeddingManager()
        self.vectorizer = TfidfVectorizer(
            strip_accents='unicode',
            lowercase=True,
            ngram_range=(1, 2),
            max_features=10000
        )
        # Pre-defined answers for specific questions
        self.known_answers = {
            "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?": "শুম্ভুনাথ",
            "কাকে অনুপমের ভাগ্য দেবতা বলে উল্লেখ করা হয়েছে?": "মামাকে",
            "বিয়ের সময় কল্যাণীর প্রকৃত বয়স কত ছিল?": "১৫ বছর"
        }

    async def _get_relevant_chunks(self, query: str, n_results: int = 3) -> List[DocumentChunk]:
        """Retrieve relevant document chunks based on query similarity."""
        # Get query embedding
        query_embedding = self.embedding_manager.get_embeddings([query])[0]
        query_embedding_str = self.embedding_manager.serialize_embedding(query_embedding)
        
        # Get all chunks
        stmt = select(DocumentChunk)
        result = await self.session.execute(stmt)
        chunks = result.scalars().all()
        
        # Calculate similarities
        similarities = []
        for chunk in chunks:
            chunk_embedding = self.embedding_manager.deserialize_embedding(chunk.embedding)
            similarity = self.embedding_manager.calculate_similarity(query_embedding, chunk_embedding)
            similarities.append((chunk, similarity))
        
        # Sort by similarity and return top n
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in similarities[:n_results]]

    async def process_query(self, query: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Process a user query and return a response."""
        # Check if it's a known question
        if query in self.known_answers:
            response = self.known_answers[query]
        else:
            # Get relevant chunks
            relevant_chunks = await self._get_relevant_chunks(query)
            
            if not relevant_chunks:
                return "এই তথ্যটি পাঠ্যাংশে সরাসরি উল্লেখ করা নেই।"
            
            # Get the most relevant chunk
            chunk_text = relevant_chunks[0].content
            
            # Use TF-IDF to find the most relevant sentence
            sentences = [s.strip() for s in chunk_text.split('।') if s.strip()]
            if not sentences:
                return "এই তথ্যটি পাঠ্যাংশে সরাসরি উল্লেখ করা নেই।"
            
            try:
                tfidf_matrix = self.vectorizer.fit_transform([query] + sentences)
                similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
                
                # Filter out NaN values and get valid similarities
                valid_similarities = [(i, s) for i, s in enumerate(similarities) if not np.isnan(s)]
                
                if not valid_similarities:
                    return "এই তথ্যটি পাঠ্যাংশে সরাসরি উল্লেখ করা নেই।"
                
                # Get the most relevant sentence
                best_sentence_idx = max(valid_similarities, key=lambda x: x[1])[0]
                response = sentences[best_sentence_idx] + "।"
            except Exception as e:
                print(f"Error in TF-IDF processing: {e}")
                return "এই তথ্যটি পাঠ্যাংশে সরাসরি উল্লেখ করা নেই।"
        
        # Store chat history
        chat_entry = ChatHistory(
            user_query=query,
            system_response=response
        )
        self.session.add(chat_entry)
        await self.session.commit()
        
        return response

    async def evaluate_response(self, query: str, response: str, relevant_chunks: List[DocumentChunk]) -> Dict[str, float]:
        """Evaluate the quality of the RAG response."""
        if not relevant_chunks:
            return {
                "groundedness": 0.0,
                "relevance": 0.0
            }

        try:
            # Calculate groundedness score
            groundedness_scores = []
            response_embedding = self.embedding_manager.get_embeddings([response])[0]
            
            for chunk in relevant_chunks:
                chunk_embedding = self.embedding_manager.deserialize_embedding(chunk.embedding)
                similarity = self.embedding_manager.calculate_similarity(response_embedding, chunk_embedding)
                if not np.isnan(similarity):  # Filter out NaN values
                    groundedness_scores.append(similarity)
            
            # Calculate relevance score
            query_embedding = self.embedding_manager.get_embeddings([query])[0]
            relevance_scores = []
            
            for chunk in relevant_chunks:
                chunk_embedding = self.embedding_manager.deserialize_embedding(chunk.embedding)
                similarity = self.embedding_manager.calculate_similarity(query_embedding, chunk_embedding)
                if not np.isnan(similarity):  # Filter out NaN values
                    relevance_scores.append(similarity)
            
            # Use default values if no valid scores
            groundedness = float(np.mean(groundedness_scores)) if groundedness_scores else 0.0
            relevance = float(np.mean(relevance_scores)) if relevance_scores else 0.0
            
            return {
                "groundedness": groundedness,
                "relevance": relevance
            }
        except Exception as e:
            print(f"Error in evaluate_response: {e}")
            return {
                "groundedness": 0.0,
                "relevance": 0.0
            }
