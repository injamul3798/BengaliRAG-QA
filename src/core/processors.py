from typing import List, Dict, Any
import numpy as np
import json
import re
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

class EmbeddingManager:
    def __init__(self):
        # Using XLM-RoBERTa for better Bengali language support
        self.model = SentenceTransformer('sentence-transformers/LaBSE')
        
    def get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a list of texts."""
        # Normalize and clean Bengali text before embedding
        cleaned_texts = [self._normalize_bengali_text(text) for text in texts]
        return self.model.encode(cleaned_texts, normalize_embeddings=True)
    
    def _normalize_bengali_text(self, text: str) -> str:
        """Normalize Bengali text by removing unnecessary spaces and fixing common issues."""
        # Remove extra spaces
        text = ' '.join(text.split())
        # Fix common Bengali text issues (you can add more normalization rules)
        text = text.replace('।', '। ')  # Add space after Bengali full stop
        text = text.replace('  ', ' ')  # Remove double spaces
        return text

    def serialize_embedding(self, embedding: np.ndarray) -> str:
        """Convert numpy array to string for storage."""
        return json.dumps(embedding.tolist())

    def deserialize_embedding(self, embedding_str: str) -> np.ndarray:
        """Convert stored string back to numpy array."""
        return np.array(json.loads(embedding_str))

    def calculate_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

class DocumentProcessor:
    def __init__(self):
        # Optimized for Bengali text with smaller chunk size and larger overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,  # Smaller chunks for precise context matching
            chunk_overlap=150,  # Large overlap to maintain context of Bengali literary references
            length_function=len,
            separators=["।।", "।", "\n\n", "\n", "!", "?", ".", " ", ","]  # Prioritize Bengali punctuation
        )

    async def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a PDF file and return chunks with metadata."""
        from langchain_community.document_loaders import PyPDFLoader
        import re

        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        chunks = []
        for page in pages:
            # Clean and normalize the text
            text = self._clean_bengali_text(page.page_content)
            
            # Split into smaller chunks
            text_chunks = self.text_splitter.split_text(text)
            
            for i, chunk in enumerate(text_chunks):
                if not chunk.strip():  # Skip empty chunks
                    continue
                    
                chunks.append({
                    'content': chunk,
                    'metadata': {
                        'page': page.metadata.get('page', 0),
                        'chunk_id': i,
                        'source': file_path,
                        'total_chunks': len(text_chunks)
                    }
                })
        
        return chunks

    def _clean_bengali_text(self, text: str) -> str:
        """Clean and normalize Bengali text."""
        # Remove unnecessary whitespace
        text = ' '.join(text.split())
        
        # Fix common OCR issues in Bengali text
        text = text.replace('।।', '।')  # Remove double dandas
        text = text.replace('..', '.')   # Remove double periods
        text = text.replace('  ', ' ')   # Remove double spaces
        
        # Add proper spacing after punctuation
        text = text.replace('।', '। ')
        text = text.replace('.', '. ')
        
        # Remove any non-Bengali, non-English characters except punctuation
        text = re.sub(r'[^\u0980-\u09FF\u0964-\u0965a-zA-Z0-9\s\.,!?।]', '', text)
        
        return text.strip()
