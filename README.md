[![Build and Push Docker Image](https://github.com/johnservinis/reranker/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/johnservinis/reranker/actions/workflows/docker-publish.yml)

# Reranking Service

A FastAPI-based reranking service using Jina's multilingual cross-encoder for document relevance scoring.

## Features

- **Multilingual Support**: Uses `jinaai/jina-reranker-v2-base-multilingual` model
- **REST API**: Simple HTTP API for reranking documents
- **Health Checks**: Built-in health monitoring
- **Model Warmup**: Automatic model warmup on startup
- **Docker Ready**: Containerized with multi-architecture support

## API Endpoints

### POST /rerank

Rerank documents based on relevance to a query.

**Request:**
```json
{
  "query": "What is machine learning?",
  "documents": [
    {"id": "doc1", "text": "Machine learning is a subset of AI..."},
    {"id": "doc2", "text": "Weather patterns are influenced by..."}
  ],
  "topN": 10
}
```

**Response:**
```json
{
  "results": [
    {"id": "doc1", "score": 0.85},
    {"id": "doc2", "score": 0.23}
  ],
  "processing_time_ms": 45.2
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model": "jinaai/jina-reranker-v2-base-multilingual"
}
```

## Environment Variables

- `RERANKER_MODEL`: Model name to use (default: `jinaai/jina-reranker-v2-base-multilingual`)

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

### Docker

```bash
# Build image
docker build -t reranker .

# Run container
docker run -p 8081:8081 reranker
```

## Docker Hub

The service is automatically built and published to Docker Hub as `johnserv/reranker` via GitHub Actions.

### Pulling the Image

```bash
docker pull johnserv/reranker:latest
```

### Tags

- `latest`: Latest build from main branch
- `develop`: Latest build from develop branch
- `v1.0.0`, `v1.0`, `v1`: Semantic version tags

## Performance

- **CPU-based**: Optimized for CPU inference
- **Throughput**: ~50-150ms per 20-50 documents (hardware dependent)
- **Memory**: ~1-2GB RAM usage
- **Scalability**: Stateless service, easily horizontally scalable

## Security

- Runs as non-root user in container
- No sensitive data logged
- Internal network deployment recommended