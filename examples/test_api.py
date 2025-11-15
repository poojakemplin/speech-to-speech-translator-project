"""
Example: Test API Endpoints
Demonstrates API usage
"""
import requests
import json


BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n1. Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")


def test_languages():
    """Test languages endpoint"""
    print("\n2. Testing Languages Endpoint...")
    response = requests.get(f"{BASE_URL}/languages")
    print(f"   Status: {response.status_code}")
    languages = response.json()
    print(f"   Supported languages: {len(languages)}")
    for lang in languages[:5]:
        print(f"   - {lang['code']}: {lang['name']}")


def test_translation():
    """Test translation endpoint"""
    print("\n3. Testing Translation Endpoint...")
    
    payload = {
        "text": "Hello! Welcome to the cricket match. The game is about to begin.",
        "source_language": "en-US",
        "target_languages": ["es-ES", "fr-FR", "hi-IN"],
        "context": "Sports commentary"
    }
    
    print(f"   Original: {payload['text']}")
    print(f"   Translating to: {', '.join(payload['target_languages'])}")
    
    response = requests.post(f"{BASE_URL}/translate", json=payload)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Latency: {result['latency']:.2f}s")
        print("   Translations:")
        for lang, text in result['translations'].items():
            print(f"   - {lang}: {text}")
    else:
        print(f"   Error: {response.text}")


def test_batch_translation():
    """Test batch translation"""
    print("\n4. Testing Batch Translation...")
    
    batch_payload = [
        {
            "text": "What a fantastic shot!",
            "source_language": "en-US",
            "target_languages": ["es-ES"]
        },
        {
            "text": "The crowd is cheering!",
            "source_language": "en-US",
            "target_languages": ["fr-FR"]
        }
    ]
    
    response = requests.post(f"{BASE_URL}/translate/batch", json=batch_payload)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        for i, result in enumerate(results):
            print(f"   {i+1}. {result['original_text']}")
            for lang, text in result['translations'].items():
                print(f"      {lang}: {text}")


def test_collection_stats():
    """Test collection stats endpoint"""
    print("\n5. Testing Collection Stats Endpoint...")
    response = requests.get(f"{BASE_URL}/stats/collection")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {json.dumps(response.json(), indent=2)}")


def main():
    """Run all API tests"""
    print("=" * 60)
    print("API Endpoint Tests")
    print("=" * 60)
    print("\nMake sure the API server is running:")
    print("  python module4_deployment/api_server.py")
    print("=" * 60)
    
    try:
        test_health()
        test_languages()
        test_translation()
        test_batch_translation()
        test_collection_stats()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API server")
        print("  Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    main()
