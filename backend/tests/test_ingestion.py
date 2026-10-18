"""
Tests for document ingestion pipeline.
"""

import pytest
import tempfile
import os
from pathlib import Path
from sqlalchemy.orm import Session

from app.ai.ingestion import DocumentIngestor
from app.models import Resource, ResourceChunk
from app.database import SessionLocal


@pytest.fixture
def db():
    """Create a test database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def ingestor():
    """Create a document ingestor."""
    return DocumentIngestor()


@pytest.fixture
def temp_corpus_dir():
    """Create a temporary directory with test documents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test TXT file
        txt_path = Path(tmpdir) / "test.txt"
        txt_path.write_text("This is a test document about stress management. "
                           "Stress is a common experience for students. "
                           "Managing stress is important for wellbeing.", encoding="utf-8")
        
        # Create a test Markdown file
        md_path = Path(tmpdir) / "test.md"
        md_path.write_text("# Study Tips\n\n"
                          "Regular breaks help maintain focus.\n"
                          "Sleep is essential for memory consolidation.", encoding="utf-8")
        
        yield tmpdir


def test_chunk_text(ingestor):
    """Test text chunking."""
    text = "This is a test. " * 100
    chunks = ingestor.chunk_text(text)
    
    assert len(chunks) > 1
    assert all(len(chunk) > 0 for chunk in chunks)
    # Check overlap
    assert ingestor.chunk_overlap > 0


def test_chunk_text_empty(ingestor):
    """Test chunking empty text."""
    chunks = ingestor.chunk_text("")
    assert chunks == []


def test_extract_text_from_txt(ingestor, temp_corpus_dir):
    """Test TXT extraction."""
    txt_path = Path(temp_corpus_dir) / "test.txt"
    text = ingestor.extract_text_from_txt(str(txt_path))
    
    assert "stress management" in text.lower()
    assert len(text) > 0


def test_extract_text_from_markdown(ingestor, temp_corpus_dir):
    """Test Markdown extraction."""
    md_path = Path(temp_corpus_dir) / "test.md"
    text = ingestor.extract_text_from_markdown(str(md_path))
    
    assert "Study Tips" in text
    assert "Regular breaks" in text


def test_ingest_document_without_embedding_model(db, ingestor, temp_corpus_dir):
    """Test document ingestion without embedding model (embedding will be None)."""
    txt_path = Path(temp_corpus_dir) / "test.txt"
    
    resource = ingestor.ingest_document(
        db=db,
        file_path=str(txt_path),
        title="Test Resource",
        category="test",
        source_url="",
        language="en",
        verification_status="internal",
        publication_date=""
    )
    
    assert resource is not None
    assert resource.title == "Test Resource"
    assert resource.category == "test"
    assert resource.language == "en"
    
    # Check chunks were created
    chunks = db.query(ResourceChunk).filter(ResourceChunk.resource_id == resource.id).all()
    assert len(chunks) > 0
    # Embeddings should be None since model is not loaded
    assert all(chunk.embedding is None for chunk in chunks)


def test_ingest_duplicate_document(db, ingestor, temp_corpus_dir):
    """Test that duplicate documents are skipped."""
    txt_path = Path(temp_corpus_dir) / "test.txt"
    
    # First ingestion
    resource1 = ingestor.ingest_document(
        db=db,
        file_path=str(txt_path),
        title="Duplicate Test",
        category="test",
        source_url="",
        language="en",
        verification_status="internal",
        publication_date=""
    )
    
    # Second ingestion with same title
    resource2 = ingestor.ingest_document(
        db=db,
        file_path=str(txt_path),
        title="Duplicate Test",
        category="test",
        source_url="",
        language="en",
        verification_status="internal",
        publication_date=""
    )
    
    assert resource1 is not None
    assert resource2 is not None
    assert resource1.id == resource2.id  # Same resource


def test_ingest_from_directory(db, ingestor, temp_corpus_dir):
    """Test batch ingestion from directory."""
    results = ingestor.ingest_from_directory(db, temp_corpus_dir)
    
    assert results["total"] == 2  # txt and md files
    assert results["success"] >= 1  # At least one should succeed
    assert results["failed"] >= 0


def test_unsupported_file_type(db, ingestor, temp_corpus_dir):
    """Test that unsupported file types are skipped."""
    # Create an unsupported file
    unsupported_path = Path(temp_corpus_dir) / "test.xyz"
    unsupported_path.write_text("content", encoding="utf-8")
    
    resource = ingestor.ingest_document(
        db=db,
        file_path=str(unsupported_path),
        title="Unsupported",
        category="test",
        source_url="",
        language="en",
        verification_status="internal",
        publication_date=""
    )
    
    assert resource is None


def test_chunk_metadata(ingestor, temp_corpus_dir, db):
    """Test that chunk metadata is stored correctly."""
    txt_path = Path(temp_corpus_dir) / "test.txt"
    
    resource = ingestor.ingest_document(
        db=db,
        file_path=str(txt_path),
        title="Metadata Test",
        category="test",
        source_url="",
        language="en",
        verification_status="internal",
        publication_date=""
    )
    
    chunks = db.query(ResourceChunk).filter(ResourceChunk.resource_id == resource.id).all()
    assert len(chunks) > 0
    
    for chunk in chunks:
        assert chunk.chunk_metadata is not None
        assert "chunk_index" in chunk.chunk_metadata
        assert "character_count" in chunk.chunk_metadata
