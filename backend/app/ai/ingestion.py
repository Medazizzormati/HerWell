"""
Document ingestion pipeline for RAG.
Supports PDF, Markdown, TXT, and optional CSV.
Handles chunking, embedding generation, and storage.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import PyPDF2

from ..models import Resource, ResourceChunk
from ..database import SessionLocal

logger = logging.getLogger(__name__)

# Multilingual embedding model - supports French, English, Arabic
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384  # Dimension for paraphrase-multilingual-MiniLM-L12-v2

class DocumentIngestor:
    """Handles document ingestion, chunking, and embedding generation."""
    
    def __init__(
        self,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = None
        self.embedding_model_name = embedding_model
        
    def load_embedding_model(self) -> bool:
        """Load the embedding model. Returns True if successful."""
        try:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info("Embedding model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            return False
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {file_path}: {e}")
        return text
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Failed to read TXT {file_path}: {e}")
            return ""
    
    def extract_text_from_markdown(self, file_path: str) -> str:
        """Extract text from Markdown file."""
        return self.extract_text_from_txt(file_path)
    
    def extract_text_from_csv(self, file_path: str) -> str:
        """Extract text from CSV file (optional)."""
        try:
            import csv
            text = ""
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    text += " ".join(row) + "\n"
            return text
        except Exception as e:
            logger.error(f"Failed to read CSV {file_path}: {e}")
            return ""
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at word boundary
            if end < text_length and not text[end].isspace():
                last_space = chunk.rfind(' ')
                if last_space > 0:
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap
            
            if start < 0:
                start = 0
        
        return [c for c in chunks if c]
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text."""
        if not self.embedding_model:
            logger.warning("Embedding model not loaded")
            return None
        
        try:
            embedding = self.embedding_model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def ingest_document(
        self,
        db: Session,
        file_path: str,
        title: str,
        category: str,
        source_url: str = "",
        language: str = "fr",
        verification_status: str = "internal",
        publication_date: str = ""
    ) -> Optional[Resource]:
        """Ingest a document into the database."""
        
        # Determine file type
        ext = Path(file_path).suffix.lower()
        
        # Extract text
        if ext == '.pdf':
            content = self.extract_text_from_pdf(file_path)
        elif ext == '.md':
            content = self.extract_text_from_markdown(file_path)
        elif ext == '.txt':
            content = self.extract_text_from_txt(file_path)
        elif ext == '.csv':
            content = self.extract_text_from_csv(file_path)
        else:
            logger.error(f"Unsupported file type: {ext}")
            return None
        
        if not content:
            logger.error(f"No content extracted from {file_path}")
            return None
        
        # Check if resource already exists
        existing = db.query(Resource).filter(Resource.title == title).first()
        if existing:
            logger.info(f"Resource '{title}' already exists, skipping")
            return existing
        
        # Create resource
        resource = Resource(
            title=title,
            category=category,
            content=content,
            source_label="Ingested document",
            source_url=source_url,
            language=language,
            verification_status=verification_status,
            publication_date=publication_date
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)
        
        # Chunk the content
        chunks = self.chunk_text(content)
        logger.info(f"Created {len(chunks)} chunks for '{title}'")
        
        # Generate embeddings and store chunks
        for idx, chunk_text in enumerate(chunks):
            embedding = self.generate_embedding(chunk_text)
            
            chunk = ResourceChunk(
                resource_id=resource.id,
                chunk_index=idx,
                content=chunk_text,
                embedding=embedding,
                chunk_metadata={
                    "chunk_index": idx,
                    "character_count": len(chunk_text),
                    "embedding_model": self.embedding_model_name if embedding else None
                }
            )
            db.add(chunk)
        
        db.commit()
        logger.info(f"Successfully ingested '{title}' with {len(chunks)} chunks")
        return resource
    
    def ingest_from_directory(
        self,
        db: Session,
        directory: str,
        metadata_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ingest all documents from a directory."""
        
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        # Load metadata if provided
        metadata_map = {}
        if metadata_file and os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_map = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metadata file: {e}")
        
        # Iterate through files
        for file_path in Path(directory).rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext not in ['.pdf', '.md', '.txt', '.csv']:
                    continue
                
                results["total"] += 1
                
                # Get metadata
                file_key = str(file_path)
                meta = metadata_map.get(file_key, {})
                
                title = meta.get('title', file_path.stem)
                category = meta.get('category', 'general')
                source_url = meta.get('source_url', '')
                language = meta.get('language', 'fr')
                verification_status = meta.get('verification_status', 'internal')
                publication_date = meta.get('publication_date', '')
                
                try:
                    self.ingest_document(
                        db=db,
                        file_path=str(file_path),
                        title=title,
                        category=category,
                        source_url=source_url,
                        language=language,
                        verification_status=verification_status,
                        publication_date=publication_date
                    )
                    results["success"] += 1
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path}: {e}")
                    results["failed"] += 1
                    results["errors"].append(f"{file_path}: {str(e)}")
        
        return results


def ingest_corpus(
    corpus_dir: str,
    metadata_file: Optional[str] = None,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL
) -> Dict[str, Any]:
    """
    Main entry point for corpus ingestion.
    
    Args:
        corpus_dir: Directory containing documents to ingest
        metadata_file: Optional JSON file with document metadata
        embedding_model: Name of the sentence-transformers model to use
    
    Returns:
        Dictionary with ingestion results
    """
    logger.info(f"Starting corpus ingestion from {corpus_dir}")
    
    # Initialize ingestor
    ingestor = DocumentIngestor(embedding_model=embedding_model)
    
    # Load embedding model
    if not ingestor.load_embedding_model():
        logger.error("Failed to load embedding model")
        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "errors": ["Failed to load embedding model"]
        }
    
    # Create database session
    db = SessionLocal()
    
    try:
        results = ingestor.ingest_from_directory(
            db=db,
            directory=corpus_dir,
            metadata_file=metadata_file
        )
        logger.info(f"Ingestion complete: {results}")
        return results
    finally:
        db.close()


if __name__ == "__main__":
    # CLI for manual ingestion
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ingestion.py <corpus_directory> [metadata_file] [embedding_model]")
        sys.exit(1)
    
    corpus_dir = sys.argv[1]
    metadata_file = sys.argv[2] if len(sys.argv) > 2 else None
    embedding_model = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_EMBEDDING_MODEL
    
    results = ingest_corpus(corpus_dir, metadata_file, embedding_model)
    print(json.dumps(results, indent=2))
