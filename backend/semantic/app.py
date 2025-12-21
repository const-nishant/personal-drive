import logging
import os
import pickle
import secrets
from threading import Lock
from typing import List

import faiss
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
INDEX_DIR = os.getenv("INDEX_DIR", "./index")
INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
META_PATH = os.path.join(INDEX_DIR, "meta.pkl")
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

# API Key Configuration
# Read from environment variable, or generate one for development
API_KEY_ENV = os.getenv("API_KEY") or os.getenv("SEMANTIC_SERVICE_API_KEY")
if API_KEY_ENV:
    API_KEY = API_KEY_ENV
    logger.info("API key loaded from environment variable")
else:
    # Generate a random API key for development (32 bytes = 64 hex characters)
    API_KEY = secrets.token_hex(32)
    logger.warning(
        f"⚠️  No API_KEY environment variable set. Generated API key for this session: {API_KEY}"
    )
    logger.warning(
        "⚠️  Set API_KEY or SEMANTIC_SERVICE_API_KEY environment variable for production!"
    )

# --- Global State (initialized at startup) ---
app = FastAPI(title="Semantic Search Service")
model = None
index = None
id_map: List[str] = []  # FAISS index → file_id
index_lock = Lock()


# --- Pydantic Models ---
class IndexRequest(BaseModel):
    file_id: str
    text: str


class SearchRequest(BaseModel):
    query: str
    k: int = 5


class SearchResponse(BaseModel):
    file_ids: List[str]


# --- API Key Authentication ---
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Verify API key from request header."""
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Provide X-API-Key header."
        )
    return x_api_key


# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """Initialize model and index on startup."""
    global model, index, id_map

    logger.info(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # Create index directory if it doesn't exist
    os.makedirs(INDEX_DIR, exist_ok=True)

    # Load or create FAISS index
    if os.path.exists(INDEX_PATH):
        logger.info(f"Loading existing index from {INDEX_PATH}")
        index = faiss.read_index(INDEX_PATH)

        # Load id_map
        if os.path.exists(META_PATH):
            with open(META_PATH, "rb") as f:
                id_map = pickle.load(f)
            logger.info(f"Loaded {len(id_map)} indexed documents")
        else:
            logger.warning("Index exists but id_map not found. Starting fresh.")
    else:
        logger.info("Creating new FAISS index")
        # Create FAISS index with L2 distance
        index = faiss.IndexFlatL2(EMBEDDING_DIM)
        logger.info("New index created successfully")


# --- Endpoints ---
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Personal Drive Semantic Search Service",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "index": "/index",
            "search": "/search"
        },
        "docs": "/docs"
    }


@app.post("/index")
async def index_document(req: IndexRequest, api_key: str = Depends(verify_api_key)):
    """Index a document with its text content."""
    global index, id_map

    # Validation
    if not req.file_id:
        raise HTTPException(status_code=400, detail="file_id is required")

    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    # Check if already indexed
    if req.file_id in id_map:
        logger.info(f"Document {req.file_id} already indexed, skipping")
        return {"status": "already_indexed"}

    try:
        # Generate embedding
        embedding = model.encode(req.text.strip(), convert_to_numpy=True, normalize_embeddings=True).reshape(1, -1)

        # Thread-safe index update
        with index_lock:
            # Add to FAISS index
            index.add(embedding)

            # Store metadata mapping
            id_map.append(req.file_id)

            # Persist to disk
            faiss.write_index(index, INDEX_PATH)
            with open(META_PATH, "wb") as f:
                pickle.dump(id_map, f)

        logger.info(f"Indexed document {req.file_id}")
        return {"status": "indexed"}

    except Exception as e:
        logger.error(f"Indexing failed for {req.file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@app.post("/search", response_model=SearchResponse)
async def search_documents(req: SearchRequest, api_key: str = Depends(verify_api_key)):
    """Search for similar documents."""
    global index, id_map

    # Validation
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")

    if req.k <= 0:
        raise HTTPException(status_code=400, detail="k must be positive")

    # Check if index is initialized
    if index is None or index.ntotal == 0:
        return SearchResponse(file_ids=[])

    try:
        # Generate query embedding
        query_embedding = model.encode(
            req.query.strip(), convert_to_numpy=True, normalize_embeddings=True
        ).reshape(1, -1)

        # Search in FAISS (thread-safe read)
        with index_lock:
            distances, indices = index.search(query_embedding, min(req.k, index.ntotal))

        # Map FAISS indices to file_ids
        file_ids = []
        for idx in indices[0]:
            if idx >= 0 and idx < len(id_map):  # Valid index within bounds
                file_ids.append(id_map[idx])

        logger.info(
            f"Search returned {len(file_ids)} results for query: {req.query[:50]}..."
        )
        return SearchResponse(file_ids=file_ids)

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    status = {
        "status": "ok",
        "model_loaded": model is not None,
        "index_initialized": index is not None,
        "index_size": index.ntotal if index else 0,
        "documents_indexed": len(id_map),
    }
    return status


@app.get("/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Get service statistics."""
    return {
        "model": MODEL_NAME,
        "embedding_dimension": EMBEDDING_DIM,
        "index_size": index.ntotal if index else 0,
        "documents_indexed": len(id_map),
        "index_path": INDEX_PATH,
        "meta_path": META_PATH,
    }
