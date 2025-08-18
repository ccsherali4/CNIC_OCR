#!/usr/bin/env python3
"""
Simple test to verify Google Vision API is working
"""

import os
import sys
from google.cloud import vision

def test_vision_api():
    """Test Google Vision API connection"""
    try:
        # Set credentials path
        credentials_path = os.path.join(os.path.dirname(__file__), 'credentials', 'service_account.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # Initialize client
        client = vision.ImageAnnotatorClient()
        print("✅ Google Vision API client created successfully!")
        
        # Test with a simple text detection (without image)
        # This will fail but confirms the API is accessible
        try:
            from google.cloud.vision import Image
            # Create empty image to test API connection
            image = Image()
            response = client.text_detection(image=image)
            print("🔗 API connection established!")
        except Exception as api_error:
            if "Empty requests are not supported" in str(api_error) or "image" in str(api_error):
                print("🔗 API connection established! (Empty request test - expected error)")
                return True
            else:
                print(f"❌ API Error: {api_error}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Vision API Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Vision API Setup")
    print("=" * 40)
    
    if test_vision_api():
        print("\n🎉 Vision API is properly configured!")
        print("You can now upload CNIC images for processing.")
    else:
        print("\n💥 Vision API setup failed!")
        print("Please check your credentials and try again.")
