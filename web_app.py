from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
import base64
import io
from datetime import datetime
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')  # Using the best model
    logger.info("Gemini AI configured successfully")
else:
    model = None
    logger.warning("Gemini API key not found. Please set GEMINI_API_KEY in .env file")

class GeminiVisionService:
    """Service for handling Gemini AI Vision operations"""
    
    def __init__(self):
        self.model = model
    
    def extract_text_from_image(self, image_file):
        """Extract text from image using Gemini Vision"""
        try:
            if not self.model:
                raise Exception("Gemini AI not configured. Please set GEMINI_API_KEY in .env file")
            
            # Convert uploaded file to PIL Image
            image = Image.open(image_file)
            
            # Create the prompt for accurate text extraction
            prompt = """
            Analyze this image carefully and extract ALL text content with maximum accuracy.
            
            Instructions:
            1. Extract every piece of text visible in the image
            2. Maintain the original formatting and structure as much as possible
            3. Include line breaks where they appear in the original
            4. If text appears in different sections, separate them clearly
            5. Be extremely precise with numbers, dates, and special characters
            6. If you see any handwritten text, include it as well
            7. If text is in multiple languages, extract all of it
            
            Please provide the extracted text exactly as it appears in the image:
            """
            
            # Generate content with the image
            response = self.model.generate_content([prompt, image])
            
            if response.text:
                return response.text.strip()
            else:
                return "No text could be extracted from the image"
        
        except Exception as e:
            logger.error(f"Gemini text extraction failed: {str(e)}")
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def extract_structured_data(self, image_file):
        """Extract structured data from image (particularly useful for CNIC)"""
        try:
            if not self.model:
                raise Exception("Gemini AI not configured")
            
            # Convert uploaded file to PIL Image
            image = Image.open(image_file)
            
            # Create detailed prompt for structured extraction
            prompt = """
            Analyze this image and extract structured information. This might be an ID card, document, or any image with text.
            
            First, extract ALL text exactly as it appears.
            
            Then, if this appears to be an ID card or official document, try to identify and structure the following information:
            - Full Name
            - ID/Card Number
            - Father's Name / Parent's Name
            - Date of Birth
            - Date of Issue
            - Date of Expiry
            - Address
            - Gender
            - Any other relevant fields
            
            Provide the response in JSON format with two sections:
            1. "raw_text": All extracted text exactly as it appears
            2. "structured_data": Key-value pairs of identified information (only include fields that are clearly visible)
            
            If it's not an ID card, still extract all text and provide any structured information you can identify.
            
            Example format:
            {
                "raw_text": "All text extracted from image...",
                "structured_data": {
                    "name": "value if found",
                    "id_number": "value if found",
                    "father_name": "value if found"
                }
            }
            """
            
            # Generate content with the image
            response = self.model.generate_content([prompt, image])
            
            if response.text:
                # Try to parse as JSON, fallback to plain text
                try:
                    import json
                    # Extract JSON from response (Gemini might include extra text)
                    response_text = response.text.strip()
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != -1:
                        json_str = response_text[start_idx:end_idx]
                        parsed_data = json.loads(json_str)
                        return parsed_data
                    else:
                        # Fallback if no JSON structure found
                        return {
                            "raw_text": response_text,
                            "structured_data": {}
                        }
                except json.JSONDecodeError:
                    # If JSON parsing fails, return as plain text
                    return {
                        "raw_text": response.text.strip(),
                        "structured_data": {}
                    }
            else:
                return {
                    "raw_text": "No text could be extracted from the image",
                    "structured_data": {}
                }
        
        except Exception as e:
            logger.error(f"Structured extraction failed: {str(e)}")
            raise Exception(f"Structured data extraction failed: {str(e)}")

# Initialize service
vision_service = GeminiVisionService()

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
        'version': '2.0.0',
        'gemini_configured': model is not None
    })

@app.route('/test-gemini', methods=['GET'])
def test_gemini():
    """Test Gemini API with world capitals question"""
    try:
        if not model:
            return jsonify({
                'success': False,
                'message': 'Gemini AI not configured. Please set GEMINI_API_KEY in .env file'
            }), 500
        
        test_question = "What are the capitals of France, Germany, Japan, and Italy? Please list them clearly."
        response = model.generate_content(test_question)
        
        return jsonify({
            'success': True,
            'message': 'Gemini API test successful',
            'test_question': test_question,
            'response': response.text,
            'model': 'gemini-1.5-pro-latest'
        })
    
    except Exception as e:
        logger.error(f"Gemini test failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Gemini test failed: {str(e)}'
        }), 500

@app.route('/api/extract-text', methods=['POST'])
def extract_text_api():
    """Extract text from uploaded image using Gemini Vision"""
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
        
        # Extract structured data using Gemini
        result = vision_service.extract_structured_data(file)
        
        return jsonify({
            'success': True,
            'message': 'Text extracted successfully',
            'data': {
                'extracted_text': result.get('raw_text', ''),
                'structured_data': result.get('structured_data', {}),
                'filename': file.filename,
                'timestamp': datetime.utcnow().isoformat(),
                'model_used': 'gemini-1.5-pro-latest'
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
            import google.generativeai
            packages_status['google_generativeai'] = "✓ Installed"
        except ImportError:
            packages_status['google_generativeai'] = "✗ Not installed"
        
        try:
            from PIL import Image
            packages_status['pillow'] = "✓ Installed"
        except ImportError:
            packages_status['pillow'] = "✗ Not installed"
        
        return jsonify({
            'success': True,
            'application_status': 'Running',
            'gemini_configured': model is not None,
            'packages': packages_status,
            'endpoints': {
                'web_interface': '/',
                'health_check': '/health',
                'test_gemini': '/test-gemini',
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
    print("🤖 Powered by Google Gemini AI")
    print("📍 Available endpoints:")
    print("   • GET  /                    - Web Interface")
    print("   • GET  /health              - Health check")
    print("   • GET  /test-gemini         - Test Gemini API")
    print("   • POST /api/extract-text    - Extract text from image")
    print("   • GET  /api/status          - API status")
    print()
    
    if model:
        print("✅ Gemini AI is configured and ready!")
    else:
        print("⚠️  Gemini AI not configured. Please set GEMINI_API_KEY in .env file")
    
    print("🌐 Web Interface: http://localhost:5000")
    print("📋 Test Gemini: http://localhost:5000/test-gemini")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
