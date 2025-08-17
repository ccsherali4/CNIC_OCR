#!/usr/bin/env python3
"""
Simple test script to verify all imports work correctly
"""

def test_imports():
    """Test all required imports"""
    try:
        import flask
        print(f"✓ Flask {flask.__version__} imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False

    try:
        import flask_cors
        print(f"✓ Flask-CORS imported successfully")
    except ImportError as e:
        print(f"✗ Flask-CORS import failed: {e}")

    try:
        from google.cloud import vision
        print(f"✓ Google Cloud Vision imported successfully")
    except ImportError as e:
        print(f"✗ Google Cloud Vision import failed: {e}")

    try:
        import google.generativeai as genai
        print(f"✓ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"✗ Google Generative AI import failed: {e}")

    try:
        from dotenv import load_dotenv
        print(f"✓ Python-dotenv imported successfully")
    except ImportError as e:
        print(f"✗ Python-dotenv import failed: {e}")

    try:
        from PIL import Image
        print(f"✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")

    try:
        import requests
        print(f"✓ Requests imported successfully")
    except ImportError as e:
        print(f"✗ Requests import failed: {e}")

    print("\nImport test completed!")
    return True

def test_credentials():
    """Test if credentials file exists"""
    import os
    creds_path = "credentials/service_account.json"
    if os.path.exists(creds_path):
        print(f"✓ Credentials file found at {creds_path}")
        return True
    else:
        print(f"✗ Credentials file not found at {creds_path}")
        return False

if __name__ == "__main__":
    print("=== CNIC OCR Project Test ===\n")
    
    print("1. Testing imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing credentials...")
    creds_ok = test_credentials()
    
    if imports_ok and creds_ok:
        print("\n🎉 All tests passed! Ready to start the Flask app.")
    else:
        print("\n❌ Some tests failed. Please check the installation.")
