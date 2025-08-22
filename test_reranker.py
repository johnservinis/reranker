#!/usr/bin/env python3
"""
Simple test script for the reranker service
"""
import requests
import json
import time

def test_reranker_service(base_url="http://localhost:8081"):
    """Test the reranker service endpoints"""
    
    print(f"Testing reranker service at {base_url}")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test rerank endpoint
    print("\n2. Testing rerank endpoint...")
    
    test_data = {
        "query": "What is machine learning?",
        "documents": [
            {
                "id": "doc1",
                "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."
            },
            {
                "id": "doc2", 
                "text": "Weather patterns are influenced by atmospheric pressure, temperature, and humidity changes throughout the seasons."
            },
            {
                "id": "doc3",
                "text": "Deep learning uses neural networks with multiple layers to process and learn from large amounts of data."
            },
            {
                "id": "doc4",
                "text": "Cooking pasta requires boiling water, adding salt, and timing the cooking process carefully."
            }
        ],
        "topN": 3
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/rerank",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Rerank test passed")
            print(f"   Processing time: {end_time - start_time:.2f}s")
            print(f"   Service reported time: {result.get('processing_time_ms', 0):.2f}ms")
            print("   Results:")
            for i, doc in enumerate(result.get('results', []), 1):
                print(f"     {i}. ID: {doc['id']}, Score: {doc['score']:.3f}")
            
            # Verify results make sense
            results = result.get('results', [])
            if len(results) >= 2:
                # doc1 and doc3 should score higher than doc2 and doc4 for ML query
                ml_docs = [r for r in results if r['id'] in ['doc1', 'doc3']]
                other_docs = [r for r in results if r['id'] in ['doc2', 'doc4']]
                
                if ml_docs and other_docs:
                    avg_ml_score = sum(d['score'] for d in ml_docs) / len(ml_docs)
                    avg_other_score = sum(d['score'] for d in other_docs) / len(other_docs)
                    
                    if avg_ml_score > avg_other_score:
                        print("✅ Relevance ranking appears correct")
                    else:
                        print("⚠️  Relevance ranking might need attention")
            
            return True
        else:
            print(f"❌ Rerank test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Rerank test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_reranker_service()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
        exit(1)