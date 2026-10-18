from pathlib import Path
import json
import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import numpy as np

from ..models import Resource, ResourceChunk, ProjectDocument

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "resources.json"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

logger = logging.getLogger(__name__)

def seed_resources(db: Session) -> None:
    """Seed resources from JSON file if database is empty."""
    if db.query(Resource).count():
        return
    items = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    for item in items:
        db.add(Resource(**item))
    db.commit()

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    a_np = np.array(a)
    b_np = np.array(b)
    dot_product = np.dot(a_np, b_np)
    norm_a = np.linalg.norm(a_np)
    norm_b = np.linalg.norm(b_np)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))

def generate_query_embedding(
    query: str,
    model: Optional[SentenceTransformer] = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL
) -> Optional[List[float]]:
    """Generate embedding for a query."""
    try:
        if model is None:
            model = SentenceTransformer(model_name)
        embedding = model.encode(query, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        return None

def retrieve_chunks_semantic(
    db: Session,
    query_embedding: List[float],
    limit: int = 5,
    similarity_threshold: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Retrieve chunks using semantic vector similarity.
    This works with embeddings stored in JSON (SQLite) or pgvector (PostgreSQL).
    """
    chunks = db.query(ResourceChunk).filter(ResourceChunk.embedding.isnot(None)).all()
    
    scored = []
    for chunk in chunks:
        if chunk.embedding:
            similarity = cosine_similarity(query_embedding, chunk.embedding)
            if similarity >= similarity_threshold:
                scored.append((similarity, chunk))
    
    scored.sort(key=lambda pair: pair[0], reverse=True)
    
    results = []
    for similarity, chunk in scored[:limit]:
        # Get parent resource for metadata
        resource = db.query(Resource).filter(Resource.id == chunk.resource_id).first()
        results.append({
            "chunk_id": chunk.id,
            "resource_id": chunk.resource_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "similarity": similarity,
            "resource_title": resource.title if resource else "Unknown",
            "resource_category": resource.category if resource else "Unknown",
            "source_label": resource.source_label if resource else "Unknown",
            "source_url": resource.source_url if resource else "",
            "language": resource.language if resource else "unknown",
            "verification_status": resource.verification_status if resource else "unknown"
        })
    
    return results

def retrieve_resources_keyword(db: Session, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Keyword-based retrieval fallback.
    Works in SQLite and PostgreSQL without requiring embeddings.
    """
    terms = [t.strip(".,!?;:()[]{}'\"").lower() for t in query.split()]
    terms = [t for t in terms if len(t) >= 3]
    resources = db.query(Resource).all()
    scored = []
    for resource in resources:
        haystack = f"{resource.title} {resource.category} {resource.content}".lower()
        score = sum(1 for term in set(terms) if term in haystack)
        if score:
            scored.append((score, resource))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [
        {
            "title": r.title,
            "category": r.category,
            "content": r.content,
            "source": r.source_label,
            "source_url": r.source_url,
            "language": r.language,
            "verification_status": r.verification_status
        }
        for score, r in scored[:limit]
    ]

def retrieve_resources(
    db: Session,
    query: str,
    limit: int = 5,
    use_semantic: bool = False,  # Disabled by default to avoid model download
    similarity_threshold: float = 0.3,
    embedding_model: Optional[SentenceTransformer] = None
) -> Dict[str, Any]:
    """
    Retrieve resources using semantic search or keyword fallback.
    
    Args:
        db: Database session
        query: User query
        limit: Maximum number of results
        use_semantic: Whether to attempt semantic search (disabled by default)
        similarity_threshold: Minimum similarity for semantic results
        embedding_model: Pre-loaded embedding model (optional)
    
    Returns:
        Dictionary with retrieval results and metadata
    """
    # Try semantic retrieval first if explicitly requested
    if use_semantic and embedding_model:
        query_embedding = generate_query_embedding(query, embedding_model)
        if query_embedding:
            chunks = retrieve_chunks_semantic(
                db, query_embedding, limit, similarity_threshold
            )
            if chunks:
                logger.info(f"Semantic retrieval returned {len(chunks)} chunks")
                return {
                    "method": "semantic",
                    "results": chunks,
                    "query_embedding": True,
                    "total_chunks": len(chunks)
                }
    
    # Fallback to keyword retrieval (default)
    logger.info("Using keyword retrieval fallback")
    resources = retrieve_resources_keyword(db, query, limit)
    return {
        "method": "keyword",
        "results": resources,
        "query_embedding": False,
        "total_chunks": len(resources)
    }

def retrieve_project_documents(
    db: Session,
    project_id: int,
    query: str,
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant project documents for the Technical PFE Assistant.
    Uses keyword matching on document content and title.
    
    Args:
        db: Database session
        project_id: Project ID to search within
        query: User query
        limit: Maximum number of results
    
    Returns:
        List of relevant project documents with metadata
    """
    docs = db.query(ProjectDocument).filter(ProjectDocument.project_id == project_id).all()
    
    if not docs:
        return []
    
    terms = [t.strip(".,!?;:()[]{}'\"").lower() for t in query.split()]
    terms = [t for t in terms if len(t) >= 3]
    
    scored = []
    for doc in docs:
        haystack = f"{doc.title} {doc.content}".lower()
        score = sum(1 for term in set(terms) if term in haystack)
        if score:
            scored.append((score, doc))
    
    scored.sort(key=lambda pair: pair[0], reverse=True)
    
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
            "file_type": doc.file_type,
            "source_type": doc.source_type,
            "language": doc.language,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "source": f"Project document: {doc.file_type}"
        }
        for score, doc in scored[:limit]
    ]
