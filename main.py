from sqlalchemy import Column, Integer, String, create_engine
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import logging
import time
import numpy as np
import faiss
import redis
from embedding_module import get_embedding  

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

#Connect to Redis
cache=redis.StrictRedis(host='localhost', port=6379, db=0)
def cache_results(key, value):
    cache.set(key, value)

def get_cached_results(key):
    result = cache.get(key)
    return eval(result) if result else None

# SQLite database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./documents.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Define the Document model
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)

# Define the User model for rate limiting
class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    api_calls = Column(Integer, default=0)

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# FAISS setup
faiss_index = faiss.IndexFlatL2(300)  # Assume 300 is the embedding dimension, adjust as needed

def populate_faiss_index(documents):
    embeddings = [get_embedding(doc.content) for doc in documents]
    faiss_index.add(np.array(embeddings).astype(np.float32))

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Middleware to log request duration
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"Request: {request.method} {request.url} completed in {process_time:.4f} seconds")
    return response

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Search endpoint with rate limiting
@app.get("/search")
async def search(text: str, user_id: str, top_k: int = 5, threshold: float = 0.8, db: Session = Depends(get_db)):
    logging.info(f"Search request: user_id={user_id}, query={text}")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    # Retrieve or create the user
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(user_id=user_id, api_calls=1)
        db.add(user)
    else:
        user.api_calls += 1

    # Rate limit check
    if user.api_calls > 5:
        logging.warning(f"Rate limit exceeded for user: {user_id}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    db.commit()
    cache_key = f"search:{text}:{user_id}:{top_k}:{threshold}"
    cached_results = get_cached_results(cache_key)
    if cached_results:
        logging.info("Cache hit")
        return {"query": text, "results": cached_results, "threshold": threshold}

    # Get the query embedding
    query_embedding = get_embedding(text)
    logging.info(f"Query embedding: {query_embedding}")

    # Perform the FAISS search
    distances, indices = faiss_index.search(np.array([query_embedding]).astype(np.float32), top_k)
    logging.info(f"FAISS search results: indices={indices}, distances={distances}")

    # Retrieve documents
    results = []
    for idx in indices[0]:  # Indices is a 2D array, we need the first row
        doc = db.query(Document).filter(Document.id == idx).first()
        if doc:
            results.append({"id": doc.id, "content": doc.content})
            logging.info(f"Found document: id={doc.id}, content={doc.content}")
    # Cache the results
    cache_results(cache_key, results)

    return {
        "query": text,
        "results": results,
        "threshold": threshold
    }

# Endpoint to add a document to the database
@app.post("/add_document")
async def add_document(content: str, db: Session = Depends(get_db)):
    new_doc = Document(content=content)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # Optionally, update FAISS index here
    doc_embedding = get_embedding(content)
    faiss_index.add(np.array([doc_embedding]).astype(np.float32))
    
    return {"id": new_doc.id, "content": new_doc.content}

# Populate FAISS index with existing documents at startup
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    documents = db.query(Document).all()
    populate_faiss_index(documents)
    db.close()
    logging.info(f"FAISS index populated with {len(documents)} documents.")
