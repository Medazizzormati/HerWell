import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = "sqlite:///./test_herwell.db"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["LLM_API_KEY"] = ""

from app.database import Base, engine
from app.models import MoodCheckin, StudyTask, Resource, ResourceChunk
from sqlalchemy.orm import Session

def pytest_configure():
    """Create all tables before running tests."""
    Base.metadata.create_all(bind=engine)
