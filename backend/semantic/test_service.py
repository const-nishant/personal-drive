"""
Test script for the Semantic Search Service.
Run this after starting the server with: uvicorn app:app --reload
"""
import os
import requests
import json

BASE_URL = "http://localhost:8000"

# Get API key from environment variable
API_KEY = os.getenv("API_KEY") or os.getenv("SEMANTIC_SERVICE_API_KEY")

# Headers for protected endpoints
def get_headers():
    """Get headers with API key if available."""
    if API_KEY:
        return {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}


def test_health():
    """Test the health check endpoint."""
    print("\n=== Testing /health ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_stats():
    """Test the stats endpoint."""
    print("\n=== Testing /stats ===")
    headers = get_headers()
    response = requests.get(f"{BASE_URL}/stats", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200


def test_index_document(file_id: str, text: str):
    """Test indexing a document."""
    print(f"\n=== Testing /index (file_id: {file_id}) ===")
    headers = get_headers()
    response = requests.post(
        f"{BASE_URL}/index",
        json={"file_id": file_id, "text": text},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    return response.status_code in [200, 201]


def test_search(query: str, k: int = 5):
    """Test searching for documents."""
    print(f"\n=== Testing /search (query: '{query}', k: {k}) ===")
    headers = get_headers()
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": query, "k": k},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200


def test_error_cases():
    """Test error handling."""
    print("\n=== Testing Error Cases ===")
    headers = get_headers()
    
    # Empty query
    print("\n1. Testing empty query...")
    response = requests.post(f"{BASE_URL}/search", json={"query": "", "k": 5}, headers=headers)
    print(f"   Status: {response.status_code} (expected 400)")
    
    # Invalid k
    print("\n2. Testing invalid k...")
    response = requests.post(f"{BASE_URL}/search", json={"query": "test", "k": -1}, headers=headers)
    print(f"   Status: {response.status_code} (expected 400)")
    
    # Missing file_id
    print("\n3. Testing missing file_id...")
    response = requests.post(f"{BASE_URL}/index", json={"file_id": "", "text": "test"}, headers=headers)
    print(f"   Status: {response.status_code} (expected 400)")
    
    # Empty text
    print("\n4. Testing empty text...")
    response = requests.post(f"{BASE_URL}/index", json={"file_id": "test123", "text": ""}, headers=headers)
    print(f"   Status: {response.status_code} (expected 400)")
    
    # Missing API key
    print("\n5. Testing missing API key...")
    response = requests.post(f"{BASE_URL}/index", json={"file_id": "test123", "text": "test"})
    print(f"   Status: {response.status_code} (expected 401)")
    
    # Invalid API key
    print("\n6. Testing invalid API key...")
    response = requests.post(
        f"{BASE_URL}/index",
        json={"file_id": "test123", "text": "test"},
        headers={"X-API-Key": "invalid_key"}
    )
    print(f"   Status: {response.status_code} (expected 401)")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Semantic Search Service Test Suite")
    print("=" * 60)
    
    if API_KEY:
        print(f"\n✓ API key found in environment variable")
    else:
        print("\n⚠️  No API_KEY environment variable set.")
        print("   Set API_KEY or SEMANTIC_SERVICE_API_KEY to test protected endpoints.")
        print("   Check server logs for generated API key if running in development mode.")
    
    # Check if server is running
    try:
        test_health()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Please start the server first with:")
        print("  cd backend/semantic")
        print("  uvicorn app:app --reload")
        return
    
    # Basic endpoints
    test_stats()
    
    # Index some test documents
    print("\n" + "=" * 60)
    print("Indexing Test Documents")
    print("=" * 60)
    
    test_documents = [
        ("doc1", "Python is a programming language used for web development and data science."),
        ("doc2", "FastAPI is a modern web framework for building APIs with Python."),
        ("doc3", "Machine learning involves training models on data to make predictions."),
        ("doc4", "Semantic search uses embeddings to find similar documents."),
        ("doc5", "FAISS is a library for efficient similarity search and clustering."),
    ]
    
    for file_id, text in test_documents:
        test_index_document(file_id, text)
    
    # Test duplicate indexing
    print("\n" + "=" * 60)
    print("Testing Duplicate Indexing")
    print("=" * 60)
    test_index_document("doc1", "This should be skipped as already indexed.")
    
    # Search tests
    print("\n" + "=" * 60)
    print("Search Tests")
    print("=" * 60)
    
    test_search("web development", k=3)
    test_search("machine learning models", k=2)
    test_search("similarity search", k=5)
    
    # Error cases
    print("\n" + "=" * 60)
    print("Error Handling Tests")
    print("=" * 60)
    test_error_cases()
    
    # Final stats
    print("\n" + "=" * 60)
    print("Final Statistics")
    print("=" * 60)
    test_stats()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

