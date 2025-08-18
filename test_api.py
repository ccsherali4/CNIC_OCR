#!/usr/bin/env python3
"""
CNIC OCR API Test Script
Test the API endpoints without Google Vision API credentials
"""

import requests
import json
import sys

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print("Health Check:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_frontend():
    """Test the frontend interface"""
    try:
        response = requests.get('http://localhost:5000/')
        print("Frontend Interface:")
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Page loaded successfully: {'Pakistani CNIC OCR' in response.text}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Frontend test failed: {e}")
        return False

def test_api_without_image():
    """Test the API endpoint without image (should return error)"""
    try:
        response = requests.post('http://localhost:5000/cnic_ocr')
        print("API Test (No Image):")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("-" * 50)
        return response.status_code == 400  # Should return 400 for missing image
    except Exception as e:
        print(f"API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing CNIC OCR Application")
    print("=" * 50)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Frontend Interface", test_frontend),
        ("API Endpoint (No Image)", test_api_without_image)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("📊 Test Results Summary:")
    print("=" * 50)
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n🎯 Overall Result:")
    if all_passed:
        print("✅ All tests passed! The application is working correctly.")
        print("\n📝 Next Steps:")
        print("1. Set up Google Vision API credentials")
        print("2. Place service_account.json in credentials/ directory")
        print("3. Test with actual CNIC images")
    else:
        print("❌ Some tests failed. Please check the application setup.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
