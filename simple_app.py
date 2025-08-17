from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'CNIC OCR API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'status': 'Ready for testing'
    })

@app.route('/test-api', methods=['GET'])
def test_api():
    """Test endpoint to verify setup and answer world capitals question"""
    try:
        # Test question about world capitals
        capitals = {
            "France": "Paris",
            "Germany": "Berlin", 
            "Japan": "Tokyo",
            "United Kingdom": "London",
            "Italy": "Rome",
            "Spain": "Madrid",
            "Canada": "Ottawa",
            "Australia": "Canberra"
        }
        
        result = "Here are some world capitals:\n"
        for country, capital in capitals.items():
            result += f"• {country}: {capital}\n"
        
        # Check if credentials file exists
        creds_path = "credentials/service_account.json"
        creds_exist = os.path.exists(creds_path)
        
        return jsonify({
            'success': True,
            'message': 'API test successful',
            'test_question': 'What are the capitals of some countries?',
            'response': result.strip(),
            'credentials_configured': creds_exist,
            'setup_status': 'Basic Flask app is working! Google Vision API packages can be installed when needed.',
            'next_steps': [
                '1. Install Google Cloud Vision: pip install google-cloud-vision',
                '2. Install Generative AI: pip install google-generativeai', 
                '3. Test OCR functionality with actual images'
            ]
        })
    
    except Exception as e:
        logger.error(f"API test failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'API test failed: {str(e)}'
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed status of the application"""
    try:
        # Check what packages are available
        packages_status = {}
        
        try:
            import flask
            packages_status['flask'] = f"✓ {flask.__version__}"
        except:
            packages_status['flask'] = "✗ Not installed"
            
        try:
            import flask_cors
            packages_status['flask_cors'] = "✓ Installed"
        except:
            packages_status['flask_cors'] = "✗ Not installed"
            
        try:
            from google.cloud import vision
            packages_status['google_cloud_vision'] = "✓ Installed"
        except:
            packages_status['google_cloud_vision'] = "✗ Not installed"
            
        try:
            import google.generativeai
            packages_status['google_generativeai'] = "✓ Installed"
        except:
            packages_status['google_generativeai'] = "✗ Not installed"
            
        try:
            from PIL import Image
            packages_status['pillow'] = "✓ Installed"
        except:
            packages_status['pillow'] = "✗ Not installed"
            
        try:
            import requests
            packages_status['requests'] = "✓ Installed"
        except:
            packages_status['requests'] = "✗ Not installed"
        
        # Check credentials
        creds_path = "credentials/service_account.json"
        creds_exist = os.path.exists(creds_path)
        
        return jsonify({
            'success': True,
            'application_status': 'Running',
            'packages': packages_status,
            'credentials': {
                'file_exists': creds_exist,
                'path': creds_path
            },
            'ready_for_ocr': packages_status.get('google_cloud_vision', '').startswith('✓')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting CNIC OCR API...")
    print("📍 Available endpoints:")
    print("   • GET  /           - Health check")
    print("   • GET  /test-api   - Test API with world capitals")
    print("   • GET  /status     - Detailed application status")
    print()
    print("🌐 Server will start at: http://localhost:5000")
    print("📋 You can test with: curl http://localhost:5000/test-api")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
