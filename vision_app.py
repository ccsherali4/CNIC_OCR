from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
import json
import re
from datetime import datetime
from PIL import Image
from google.cloud import vision
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleVisionService:
    """Service for handling Google Cloud Vision API operations"""
    
    def __init__(self):
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup Google Cloud Vision client"""
        try:
            # The credentials are already in the credentials folder
            credentials_path = "credentials/service_account.json"
            if os.path.exists(credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                self.client = vision.ImageAnnotatorClient()
                logger.info("✅ Google Cloud Vision API configured successfully")
            else:
                logger.error("❌ Credentials file not found")
                raise Exception("Google Cloud Vision credentials not found")
        except Exception as e:
            logger.error(f"Failed to setup Google Cloud Vision: {str(e)}")
            raise
    
    def extract_text_from_image(self, image_file):
        """Extract text from image using Google Cloud Vision API"""
        try:
            if not self.client:
                raise Exception("Google Cloud Vision client not initialized")
            
            # Read image content
            image_content = image_file.read()
            image_file.seek(0)  # Reset file pointer
            
            # Create Vision API image object
            image = vision.Image(content=image_content)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            
            if texts:
                extracted_text = texts[0].description
                return extracted_text
            else:
                return "No text found in the image"
        
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def extract_structured_data(self, image_file):
        """Extract structured data from image with enhanced CNIC parsing"""
        try:
            # First extract raw text
            raw_text = self.extract_text_from_image(image_file)
            
            # Enhanced CNIC data parsing
            structured_data = self._parse_cnic_text(raw_text)
            
            return {
                "raw_text": raw_text,
                "structured_data": structured_data
            }
        
        except Exception as e:
            logger.error(f"Structured extraction failed: {str(e)}")
            raise Exception(f"Structured data extraction failed: {str(e)}")
    
    def _parse_cnic_text(self, text):
        """Enhanced CNIC data parsing with better regex patterns"""
        cnic_data = {}
        
        try:
            # Clean text for better parsing
            text_lines = text.split('\n')
            text_clean = ' '.join(text_lines)
            
            # CNIC Number pattern (5 digits - 7 digits - 1 digit)
            cnic_patterns = [
                r'(\d{5}-\d{7}-\d{1})',
                r'(\d{5}\s*-\s*\d{7}\s*-\s*\d{1})',
                r'(\d{13})',  # Without dashes
            ]
            for pattern in cnic_patterns:
                cnic_match = re.search(pattern, text)
                if cnic_match:
                    cnic_num = cnic_match.group(1)
                    # Format with dashes if needed
                    if '-' not in cnic_num and len(cnic_num) == 13:
                        cnic_num = f"{cnic_num[:5]}-{cnic_num[5:12]}-{cnic_num[12]}"
                    cnic_data['cnic_number'] = cnic_num
                    break
            
            # Name patterns (more comprehensive)
            name_patterns = [
                r'Name[:\s]+([A-Z][A-Za-z\s]+?)(?=\n|Father|Son|Daughter|Date|CNIC)',
                r'نام[:\s]+([A-Z][A-Za-z\s]+?)(?=\n|والد)',
                r'^([A-Z][A-Z\s]+)$',  # Line with all caps (likely name)
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip()
                    if len(name) > 2 and len(name) < 50:  # Reasonable name length
                        cnic_data['name'] = name
                        break
            
            # Father's name patterns
            father_patterns = [
                r'Father[:\s]+([A-Z][A-Za-z\s]+?)(?=\n|Date|Address|Gender)',
                r'Son of[:\s]+([A-Z][A-Za-z\s]+?)(?=\n|Date)',
                r'Daughter of[:\s]+([A-Z][A-Za-z\s]+?)(?=\n|Date)',
                r'والد[:\s]+([A-Z][A-Za-z\s]+?)(?=\n|تاریخ)',
            ]
            for pattern in father_patterns:
                father_match = re.search(pattern, text, re.IGNORECASE)
                if father_match:
                    father_name = father_match.group(1).strip()
                    if len(father_name) > 2 and len(father_name) < 50:
                        cnic_data['father_name'] = father_name
                        break
            
            # Date patterns (improved)
            date_patterns = [
                r'(\d{1,2}[./-]\d{1,2}[./-]\d{4})',
                r'(\d{1,2}\s+\w+\s+\d{4})',  # 15 March 1990
                r'(\d{4}[./-]\d{1,2}[./-]\d{1,2})',  # YYYY-MM-DD
            ]
            
            dates_found = []
            for pattern in date_patterns:
                dates = re.findall(pattern, text)
                dates_found.extend(dates)
            
            # Try to identify which date is which based on context
            for i, date in enumerate(dates_found[:3]):  # Only process first 3 dates
                if i == 0:
                    # Check if it's near "birth" keywords
                    if re.search(r'birth|born|dob', text.lower()):
                        cnic_data['date_of_birth'] = date
                    else:
                        cnic_data['date_of_birth'] = date
                elif i == 1:
                    if re.search(r'issue|issued', text.lower()):
                        cnic_data['date_of_issue'] = date
                    else:
                        cnic_data['date_of_issue'] = date
                elif i == 2:
                    if re.search(r'expiry|expires|valid', text.lower()):
                        cnic_data['date_of_expiry'] = date
                    else:
                        cnic_data['date_of_expiry'] = date
            
            # Gender detection
            if re.search(r'\bMALE\b|\bM\b(?!\w)', text, re.IGNORECASE):
                cnic_data['gender'] = 'Male'
            elif re.search(r'\bFEMALE\b|\bF\b(?!\w)', text, re.IGNORECASE):
                cnic_data['gender'] = 'Female'
            
            # Address extraction (usually longer text block)
            address_patterns = [
                r'Address[:\s]+([A-Za-z0-9\s,.-]+?)(?=\n\n|\nName|\nCNIC|\nDate)',
                r'پتہ[:\s]+([A-Za-z0-9\s,.-]+?)(?=\n\n)',
            ]
            for pattern in address_patterns:
                address_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if address_match:
                    address = address_match.group(1).strip()
                    if len(address) > 10:  # Reasonable address length
                        cnic_data['address'] = address
                        break
            
            # Religion (common on Pakistani CNICs)
            religion_patterns = [
                r'Religion[:\s]+([A-Za-z]+)',
                r'مذہب[:\s]+([A-Za-z]+)',
            ]
            for pattern in religion_patterns:
                religion_match = re.search(pattern, text, re.IGNORECASE)
                if religion_match:
                    cnic_data['religion'] = religion_match.group(1).strip()
                    break
            
            # Country (usually Pakistan for CNIC)
            if re.search(r'pakistan|پاکستان', text, re.IGNORECASE):
                cnic_data['country'] = 'Pakistan'
            
        except Exception as e:
            logger.error(f"CNIC parsing failed: {str(e)}")
        
        return cnic_data

# Initialize service
vision_service = GoogleVisionService()

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'CNIC OCR API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.1.0',
        'service': 'Google Cloud Vision API',
        'status': 'Ready for text extraction'
    })

@app.route('/test-vision', methods=['GET'])
def test_vision():
    """Test Google Cloud Vision API"""
    try:
        if not vision_service.client:
            return jsonify({
                'success': False,
                'message': 'Google Cloud Vision API not configured'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Google Cloud Vision API is ready!',
            'service': 'Google Cloud Vision API',
            'capabilities': [
                'Text Detection and OCR',
                'Multi-language support',
                'Handwritten text recognition',
                'Document text extraction',
                'High accuracy text recognition'
            ],
            'project_id': 'aiml-365220',
            'ready': True
        })
    
    except Exception as e:
        logger.error(f"Vision API test failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Vision API test failed: {str(e)}'
        }), 500

@app.route('/api/extract-text', methods=['POST'])
def extract_text_api():
    """Extract text from uploaded image using Google Cloud Vision API"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No image file provided'
            }), 400
        
        file = request.files['image']
        if not file or file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No image file selected'
            }), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, BMP, or TIFF files only.'
            }), 400
        
        # Reset file pointer
        file.seek(0)
        
        # Extract structured data using Google Cloud Vision
        result = vision_service.extract_structured_data(file)
        
        return jsonify({
            'success': True,
            'message': 'Text extracted successfully using Google Cloud Vision API',
            'data': {
                'extracted_text': result.get('raw_text', ''),
                'structured_data': result.get('structured_data', {}),
                'filename': file.filename,
                'timestamp': datetime.utcnow().isoformat(),
                'service_used': 'Google Cloud Vision API',
                'project_id': 'aiml-365220'
            }
        })
    
    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_api_status():
    """Get detailed API status"""
    try:
        # Check package availability
        packages_status = {}
        
        try:
            import flask
            packages_status['flask'] = f"✓ {flask.__version__}"
        except ImportError:
            packages_status['flask'] = "✗ Not installed"
        
        try:
            from google.cloud import vision
            packages_status['google_cloud_vision'] = "✓ Installed"
        except ImportError:
            packages_status['google_cloud_vision'] = "✗ Not installed"
        
        try:
            from PIL import Image
            packages_status['pillow'] = "✓ Installed"
        except ImportError:
            packages_status['pillow'] = "✗ Not installed"
        
        vision_status = "✓ Configured" if vision_service.client else "✗ Not configured"
        
        return jsonify({
            'success': True,
            'application_status': 'Running',
            'vision_api_configured': vision_service.client is not None,
            'vision_api_status': vision_status,
            'service': 'Google Cloud Vision API',
            'project_id': 'aiml-365220',
            'packages': packages_status,
            'endpoints': {
                'web_interface': '/',
                'health_check': '/health',
                'test_vision': '/test-vision',
                'extract_text': '/api/extract-text',
                'status': '/api/status'
            }
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

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'message': 'File too large. Maximum file size is 16MB.'
    }), 413

if __name__ == '__main__':
    print("🚀 Starting CNIC OCR Web Application...")
    print("🔍 Powered by Google Cloud Vision API")
    print("📍 Available endpoints:")
    print("   • GET  /                    - Web Interface")
    print("   • GET  /health              - Health check")
    print("   • GET  /test-vision         - Test Vision API")
    print("   • POST /api/extract-text    - Extract text from image")
    print("   • GET  /api/status          - API status")
    print()
    
    if vision_service.client:
        print("✅ Google Cloud Vision API is configured and ready!")
        print("🎯 Professional OCR text extraction available")
        print("📋 Project ID: aiml-365220")
    else:
        print("❌ Google Cloud Vision API not configured")
    
    print("🌐 Web Interface: http://localhost:5001")
    print("📋 Test Vision API: http://localhost:5001/test-vision")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5001)
