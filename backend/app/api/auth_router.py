from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib
import jwt
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = settings.llm_api_key or "balance-ai-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = ""

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    from ..database import User
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate token
    access_token = create_access_token(data={"sub": new_user.email, "user_id": new_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name
        }
    }

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return token"""
    from ..database import User
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": db_user.email, "user_id": db_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name
        }
    }

@router.get("/me")
async def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current user from token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    from ..database import User
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }
