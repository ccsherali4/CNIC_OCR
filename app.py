from flask import Flask, request, jsonify, render_template
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
def index():
    """Main web interface for CNIC OCR"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({
        'message': 'CNIC OCR API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'status': 'healthy'
    })

@app.route('/cnic_ocr', methods=['POST'])
def extract_cnic_data():
    """Extract structured data from CNIC image using Document OCR"""
    try:
        # Validate request
        if 'image' not in request.files:
            return error_response('No image file provided. Please upload a CNIC image.', 400)
        
        file = request.files['image']
        if not validate_image_file(file):
            return error_response('Invalid image file. Please upload a valid image (PNG, JPG, JPEG)', 400)
        
        logger.info(f"Processing CNIC image: {file.filename}")
        
        # Process CNIC using document OCR
        cnic_data = vision_service.extract_cnic_data(file)
        
        # Calculate confidence score based on extracted fields
        parsed_data = cnic_data.get('parsed_data', {})
        total_fields = len([k for k in parsed_data.keys() if k != 'signature_present'])  # Exclude signature from count
        filled_fields = sum(1 for k, v in parsed_data.items() if k != 'signature_present' and v is not None and v != '')
        confidence_score = round((filled_fields / total_fields) * 100, 2) if total_fields > 0 else 0
        
        response_data = {
            'success': True,
            'message': 'CNIC data extracted successfully',
            'data': {
                'identity_number': parsed_data.get('identity_number'),
                'name': parsed_data.get('name'),
                'father_name': parsed_data.get('father_name'),
                'gender': parsed_data.get('gender'),
                'country_of_stay': parsed_data.get('country_of_stay'),
                'date_of_birth': parsed_data.get('date_of_birth'),
                'date_of_issue': parsed_data.get('date_of_issue'),
                'date_of_expiry': parsed_data.get('date_of_expiry')
            },
            'metadata': {
                'filename': file.filename,
                'confidence_score': confidence_score,
                'fields_extracted': filled_fields,
                'total_fields': total_fields,
                'timestamp': datetime.utcnow().isoformat(),
                'processing_method': 'Document OCR'
            },
            'raw_text': cnic_data.get('raw_text', '')
        }
        
        return jsonify(response_data), 200
    
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
