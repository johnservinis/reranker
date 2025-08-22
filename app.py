from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from sentence_transformers import CrossEncoder
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reranking Service",
    description="A FastAPI service for reranking documents using Jina multilingual cross-encoder",
    version="1.0.0"
)

# Initialize the reranker model
model_name = os.getenv("RERANKER_MODEL", "jinaai/jina-reranker-v2-base-multilingual")
logger.info(f"Loading reranker model: {model_name}")
model = CrossEncoder(model_name, trust_remote_code=True)
logger.info("Reranker model loaded successfully")


class Doc(BaseModel):
    id: str = Field(..., description="Unique identifier for the document")
    text: str = Field(..., description="Text content of the document")


class RerankRequest(BaseModel):
    query: str = Field(..., description="The query to rerank documents against")
    documents: List[Doc] = Field(..., description="List of documents to rerank")
    topN: Optional[int] = Field(None, description="Number of top results to return")


class RerankResult(BaseModel):
    id: str = Field(..., description="Document ID")
    score: float = Field(..., description="Relevance score (higher is more relevant)")


class RerankResponse(BaseModel):
    results: List[RerankResult] = Field(..., description="Reranked documents with scores")
    processing_time_ms: float = Field(..., description="Time taken to process the request in milliseconds")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model": model_name}


@app.post("/rerank", response_model=RerankResponse)
async def rerank(req: RerankRequest):
    """
    Rerank documents based on relevance to the query.
    
    Returns documents sorted by relevance score (highest first).
    """
    try:
        start_time = time.time()
        
        if not req.documents:
            raise HTTPException(status_code=400, detail="No documents provided")
        
        if not req.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Reranking {len(req.documents)} documents for query: {req.query[:100]}...")
        
        # Prepare query-document pairs for the model
        pairs = [(req.query, doc.text) for doc in req.documents]
        
        # Get relevance scores from the model
        scores = model.predict(pairs)
        
        # Combine documents with scores and sort by relevance
        results = [
            {"id": doc.id, "score": float(score)}
            for doc, score in zip(req.documents, scores)
        ]
        
        # Sort by score in descending order (highest relevance first)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply topN filtering if specified
        if req.topN is not None and req.topN > 0:
            results = results[:req.topN]
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        logger.info(f"Reranking completed in {processing_time:.2f}ms, returning {len(results)} results")
        
        return RerankResponse(
            results=results,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error during reranking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Reranking failed: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Perform model warmup on startup"""
    logger.info("Performing model warmup...")
    try:
        # Dummy prediction to warm up the model
        dummy_pairs = [("warmup query", "warmup document")]
        model.predict(dummy_pairs)
        logger.info("Model warmup completed successfully")
    except Exception as e:
        logger.error(f"Model warmup failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)