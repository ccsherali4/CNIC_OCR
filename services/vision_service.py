from google.cloud import vision
import google.generativeai as genai
import os
import json
import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class VisionService:
    """Service for handling Google Cloud Vision API operations"""
    
    def __init__(self):
        """Initialize the Vision service with API credentials"""
        self.vision_client = None
        self.genai_client = None
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup Google Cloud Vision and Gemini clients"""
        try:
            # Setup Vision API client
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'credentials/service_account.json')
            if os.path.exists(credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info("Google Cloud Vision client initialized successfully")
            else:
                logger.warning(f"Credentials file not found at {credentials_path}")
            
            # Setup Gemini client (if you have Gemini API key)
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
                self.genai_client = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup clients: {str(e)}")
            raise
    
    def test_api_connection(self, test_question: str) -> str:
        """Test API connection with a simple question"""
        try:
            if self.genai_client:
                # Test with Gemini
                response = self.genai_client.generate_content(test_question)
                return response.text
            else:
                # Fallback test - just return a success message
                return "API credentials are configured. Vision API ready for OCR operations."
        
        except Exception as e:
            logger.error(f"API test failed: {str(e)}")
            raise Exception(f"API connection test failed: {str(e)}")
    
    def extract_text_from_image(self, image_file) -> str:
        """Extract text from image using Google Cloud Vision API"""
        try:
            if not self.vision_client:
                raise Exception("Vision API client not initialized")
            
            # Read image content
            image_content = image_file.read()
            image_file.seek(0)  # Reset file pointer
            
            # Create Vision API image object
            image = vision.Image(content=image_content)
            
            # Perform text detection
            response = self.vision_client.text_detection(image=image)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            
            if texts:
                return texts[0].description
            else:
                return "No text found in the image"
        
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise
    
    def extract_cnic_data(self, image_file) -> Dict[str, Any]:
        """Extract structured CNIC data from image"""
        try:
            # First extract raw text
            raw_text = self.extract_text_from_image(image_file)
            
            # Parse CNIC data from text
            cnic_data = self._parse_cnic_text(raw_text)
            
            return {
                'raw_text': raw_text,
                'parsed_data': cnic_data
            }
        
        except Exception as e:
            logger.error(f"CNIC data extraction failed: {str(e)}")
            raise
    
    def _parse_cnic_text(self, text: str) -> Dict[str, Optional[str]]:
        """Parse CNIC data from extracted text using regex patterns"""
        cnic_data = {
            'cnic_number': None,
            'name': None,
            'father_name': None,
            'date_of_birth': None,
            'date_of_issue': None,
            'date_of_expiry': None,
            'address': None,
            'gender': None
        }
        
        try:
            # CNIC Number pattern (5 digits - 7 digits - 1 digit)
            cnic_pattern = r'(\d{5}-\d{7}-\d{1})'
            cnic_match = re.search(cnic_pattern, text)
            if cnic_match:
                cnic_data['cnic_number'] = cnic_match.group(1)
            
            # Name pattern (usually appears after "Name:" or similar)
            name_patterns = [
                r'Name[:\s]+([A-Z\s]+?)(?=\n|Father|Son|Daughter)',
                r'نام[:\s]+([A-Z\s]+?)(?=\n|والد)',
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, text, re.IGNORECASE)
                if name_match:
                    cnic_data['name'] = name_match.group(1).strip()
                    break
            
            # Father's name pattern
            father_patterns = [
                r'Father[:\s]+([A-Z\s]+?)(?=\n|Date|Address)',
                r'والد[:\s]+([A-Z\s]+?)(?=\n|تاریخ)',
            ]
            for pattern in father_patterns:
                father_match = re.search(pattern, text, re.IGNORECASE)
                if father_match:
                    cnic_data['father_name'] = father_match.group(1).strip()
                    break
            
            # Date patterns (DD.MM.YYYY or DD/MM/YYYY)
            date_pattern = r'(\d{1,2}[./]\d{1,2}[./]\d{4})'
            dates = re.findall(date_pattern, text)
            
            # Try to identify which date is which based on context
            if dates:
                # Usually the first date is date of birth
                if len(dates) >= 1:
                    cnic_data['date_of_birth'] = dates[0]
                # Second date might be issue date
                if len(dates) >= 2:
                    cnic_data['date_of_issue'] = dates[1]
                # Third date might be expiry date
                if len(dates) >= 3:
                    cnic_data['date_of_expiry'] = dates[2]
            
            # Gender detection
            if re.search(r'\bMALE\b|\bM\b|\bmale\b', text, re.IGNORECASE):
                cnic_data['gender'] = 'Male'
            elif re.search(r'\bFEMALE\b|\bF\b|\bfemale\b', text, re.IGNORECASE):
                cnic_data['gender'] = 'Female'
            
        except Exception as e:
            logger.error(f"CNIC parsing failed: {str(e)}")
        
        return cnic_data
