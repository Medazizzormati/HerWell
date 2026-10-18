"""
Document ingestion script for HERwell AI RAG system.

This script ingests documents from various sources into the pgvector database.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag import RAGPipeline
from app.config import settings
import requests
from bs4 import BeautifulSoup
import PyPDF2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize RAG pipeline
rag = RAGPipeline(settings.database_url, settings.embedding_model)
rag.create_pgvector_tables()
rag.load_model()

def ingest_url(url, title, category, source_label, source_url, language="fr"):
    """
    Ingest content from a URL.
    
    Args:
        url: URL to fetch
        title: Document title
        category: Category (wellbeing, technical, etc.)
        source_label: Source name (WHO, NHS, etc.)
        source_url: Canonical URL
        language: Document language
    """
    try:
        logger.info(f"Fetching: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up text
        text = ' '.join(text.split())
        
        if len(text) < 100:
            logger.warning(f"Content too short for {title}")
            return
        
        # Insert resource into database first
        # Note: This assumes the resources table exists
        # You'll need to insert the resource first, then get its ID
        
        # For now, we'll assume resource_id is passed
        resource_id = 1  # This should be replaced with actual insertion
        
        logger.info(f"Ingesting {title} ({len(text)} characters)")
        rag.ingest_document(
            resource_id=resource_id,
            title=title,
            content=text,
            chunk_size=500,
            overlap=50
        )
        
        logger.info(f"Successfully ingested: {title}")
        
    except Exception as e:
        logger.error(f"Failed to ingest {url}: {e}")

def ingest_pdf(path, title, category, source_label, language="en"):
    """
    Ingest content from a PDF file.
    
    Args:
        path: Path to PDF file
        title: Document title
        category: Category
        source_label: Source name
        language: Document language
    """
    try:
        logger.info(f"Reading PDF: {path}")
        
        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num, page in enumerate(reader.pages):
                text += f"\n\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
        
        text = ' '.join(text.split())
        
        if len(text) < 100:
            logger.warning(f"Content too short for {title}")
            return
        
        resource_id = 2  # This should be replaced with actual insertion
        
        logger.info(f"Ingesting {title} ({len(text)} characters)")
        rag.ingest_document(
            resource_id=resource_id,
            title=title,
            content=text,
            chunk_size=500,
            overlap=50
        )
        
        logger.info(f"Successfully ingested: {title}")
        
    except Exception as e:
        logger.error(f"Failed to ingest {path}: {e}")

def ingest_text(text, title, category, source_label, language="fr"):
    """
    Ingest raw text content.
    
    Args:
        text: Text content
        title: Document title
        category: Category
        source_label: Source name
        language: Document language
    """
    try:
        text = ' '.join(text.split())
        
        if len(text) < 100:
            logger.warning(f"Content too short for {title}")
            return
        
        resource_id = 3  # This should be replaced with actual insertion
        
        logger.info(f"Ingesting {title} ({len(text)} characters)")
        rag.ingest_document(
            resource_id=resource_id,
            title=title,
            content=text,
            chunk_size=500,
            overlap=50
        )
        
        logger.info(f"Successfully ingested: {title}")
        
    except Exception as e:
        logger.error(f"Failed to ingest {title}: {e}")

def main():
    """Main ingestion function."""
    logger.info("Starting document ingestion...")
    
    # Women's Health Documents
    logger.info("Ingesting women's health documents...")
    
    # WHO Menstrual Health
    ingest_url(
        url="https://www.who.int/news-room/fact-sheets/detail/menstrual-health",
        title="WHO Menstrual Health Fact Sheet",
        category="wellbeing",
        source_label="WHO",
        source_url="https://www.who.int/news-room/fact-sheets/detail/menstrual-health",
        language="en"
    )
    
    # Technical Documentation placeholders
    # Note: These would require the actual PDF files or proper URLs
    
    logger.info("Document ingestion complete!")

if __name__ == "__main__":
    main()
