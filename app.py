from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import our modules
from config.config import Config
from services.vision_service import VisionService
from utils.validators import validate_image_file
from utils.response_helpers import success_response, error_response

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
vision_service = VisionService()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({
        'message': 'CNIC OCR API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/test-api', methods=['GET'])
def test_api():
    """Test endpoint to verify API key works by asking for world capitals"""
    try:
        # Test with a simple question about world capitals
        test_question = "What are the capitals of France, Germany, and Japan?"
        result = vision_service.test_api_connection(test_question)
        
        return success_response({
            'message': 'API test successful',
            'test_question': test_question,
            'response': result
        })
    
    except Exception as e:
        logger.error(f"API test failed: {str(e)}")
        return error_response(f"API test failed: {str(e)}", 500)

@app.route('/ocr/extract', methods=['POST'])
def extract_text():
    """Extract text from uploaded image"""
    try:
        # Validate request
        if 'image' not in request.files:
            return error_response('No image file provided', 400)
        
        file = request.files['image']
        if not validate_image_file(file):
            return error_response('Invalid image file. Please upload a valid image (PNG, JPG, JPEG)', 400)
        
        # Process image
        extracted_text = vision_service.extract_text_from_image(file)
        
        return success_response({
            'extracted_text': extracted_text,
            'filename': file.filename,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        return error_response(f"Text extraction failed: {str(e)}", 500)

@app.route('/ocr/cnic', methods=['POST'])
def extract_cnic_data():
    """Extract structured data from CNIC image"""
    try:
        # Validate request
        if 'image' not in request.files:
            return error_response('No image file provided', 400)
        
        file = request.files['image']
        if not validate_image_file(file):
            return error_response('Invalid image file. Please upload a valid image (PNG, JPG, JPEG)', 400)
        
        # Process CNIC
        cnic_data = vision_service.extract_cnic_data(file)
        
        return success_response({
            'cnic_data': cnic_data,
            'filename': file.filename,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"CNIC extraction failed: {str(e)}")
        return error_response(f"CNIC extraction failed: {str(e)}", 500)

@app.errorhandler(404)
def not_found(error):
    return error_response('Endpoint not found', 404)

@app.errorhandler(500)
def internal_error(error):
    return error_response('Internal server error', 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
