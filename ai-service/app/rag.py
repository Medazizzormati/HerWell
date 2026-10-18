import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class RAGPipeline:
    """RAG pipeline with pgvector for semantic search."""
    
    def __init__(self, database_url: str, embedding_model: str):
        self.engine = create_engine(database_url)
        self.embedding_model_name = embedding_model
        self.model = None
        self.embedding_dim = None
        
    def load_model(self):
        """Load embedding model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.model = SentenceTransformer(self.embedding_model_name)
            # Get embedding dimension
            test_embedding = self.model.encode("test")
            self.embedding_dim = len(test_embedding)
            logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if self.model is None:
            self.load_model()
        embedding = self.model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()
    
    def create_pgvector_tables(self):
        """Create pgvector tables for RAG."""
        with self.engine.begin() as conn:
            # Enable pgvector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # Create resource_chunks table with vector column
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS resource_chunks (
                    id SERIAL PRIMARY KEY,
                    resource_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(384),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create index on embedding
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS resource_chunks_embedding_idx 
                ON resource_chunks USING ivfflat (embedding vector_cosine_ops)
            """))
            
            logger.info("pgvector tables created successfully")
    
    def ingest_document(self, resource_id: int, title: str, content: str, chunk_size: int = 500, overlap: int = 50):
        """
        Ingest a document into RAG system.
        
        Args:
            resource_id: Resource ID
            title: Document title
            content: Document content
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
        """
        if self.model is None:
            self.load_model()
        
        # Split content into chunks
        chunks = self._chunk_text(content, chunk_size, overlap)
        
        with Session(self.engine) as session:
            for i, chunk in enumerate(chunks):
                embedding = self.generate_embedding(chunk)
                session.execute(text("""
                    INSERT INTO resource_chunks (resource_id, chunk_index, content, embedding)
                    VALUES (:resource_id, :chunk_index, :content, :embedding::vector)
                """), {
                    "resource_id": resource_id,
                    "chunk_index": i,
                    "content": chunk,
                    "embedding": embedding
                })
            session.commit()
        
        logger.info(f"Ingested {len(chunks)} chunks for resource {resource_id}")
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk:
                chunks.append(chunk)
            start = end - overlap
        return chunks
    
    def search(self, query: str, limit: int = 5, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Perform semantic search using pgvector.
        
        Args:
            query: Search query
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of relevant chunks with metadata
        """
        if self.model is None:
            self.load_model()
        
        query_embedding = self.generate_embedding(query)
        
        with Session(self.engine) as session:
            # pgvector similarity search
            results = session.execute(text("""
                SELECT 
                    rc.id,
                    rc.resource_id,
                    rc.chunk_index,
                    rc.content,
                    1 - (rc.embedding <=> :embedding::vector) as similarity
                FROM resource_chunks rc
                WHERE 1 - (rc.embedding <=> :embedding::vector) > :threshold
                ORDER BY rc.embedding <=> :embedding::vector
                LIMIT :limit
            """), {
                "embedding": query_embedding,
                "threshold": similarity_threshold,
                "limit": limit
            }).fetchall()
            
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "chunk_id": row[0],
                    "resource_id": row[1],
                    "chunk_index": row[2],
                    "content": row[3],
                    "similarity": float(row[4])
                })
            
            return formatted_results
    
    def retrieve_with_metadata(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve chunks with full resource metadata.
        """
        if self.model is None:
            self.load_model()
        
        query_embedding = self.generate_embedding(query)
        
        with Session(self.engine) as session:
            results = session.execute(text("""
                SELECT 
                    rc.id,
                    rc.resource_id,
                    rc.chunk_index,
                    rc.content,
                    r.title,
                    r.category,
                    r.source_label,
                    r.source_url,
                    r.language,
                    r.verification_status,
                    1 - (rc.embedding <=> :embedding::vector) as similarity
                FROM resource_chunks rc
                JOIN resources r ON rc.resource_id = r.id
                ORDER BY rc.embedding <=> :embedding::vector
                LIMIT :limit
            """), {
                "embedding": query_embedding,
                "limit": limit
            }).fetchall()
            
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "chunk_id": row[0],
                    "resource_id": row[1],
                    "chunk_index": row[2],
                    "content": row[3],
                    "resource_title": row[4],
                    "resource_category": row[5],
                    "source_label": row[6],
                    "source_url": row[7],
                    "language": row[8],
                    "verification_status": row[9],
                    "similarity": float(row[10])
                })
            
            return formatted_results
