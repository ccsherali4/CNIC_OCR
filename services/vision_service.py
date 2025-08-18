from google.cloud import vision
import os
import json
import re
from typing import Dict, Any, Optional
import logging
import io
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

# Try to import Gemini AI - optional
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class VisionService:
    """Enhanced service for handling Google Cloud Vision API operations with improved CNIC extraction"""
    
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
            
            # Convert relative path to absolute path
            if not os.path.isabs(credentials_path):
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                credentials_path = os.path.join(current_dir, credentials_path)
            
            if os.path.exists(credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info(f"Google Cloud Vision client initialized successfully with credentials from {credentials_path}")
            else:
                logger.error(f"Credentials file not found at {credentials_path}")
                raise Exception(f"Credentials file not found at {credentials_path}")
            
            # Setup Gemini client (if available and API key provided)
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
            if gemini_api_key and GEMINI_AVAILABLE:
                genai.configure(api_key=gemini_api_key)
                self.genai_client = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini client initialized successfully")
            else:
                if not GEMINI_AVAILABLE:
                    logger.info("Gemini AI not available (package not installed)")
                else:
                    logger.info("Gemini API key not provided, skipping Gemini setup")
            
        except Exception as e:
            logger.error(f"Failed to setup clients: {str(e)}")
            raise
    
    def preprocess_image_for_ocr(self, image_data):
        """Preprocess image for better OCR accuracy"""
        try:
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too small (min 1200px width for optimal OCR)
            width, height = image.size
            if width < 1200:
                ratio = 1200 / width
                new_width = 1200
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            # Enhance contrast and sharpness
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.3)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Convert to OpenCV format for advanced processing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Apply Gaussian blur to reduce noise
            cv_image = cv2.GaussianBlur(cv_image, (1, 1), 0)
            
            # Apply denoising
            cv_image = cv2.fastNlMeansDenoisingColored(cv_image, None, 10, 10, 7, 21)
            
            # Convert to grayscale for better text detection
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding for better text clarity
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Convert back to color image
            cv_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            
            # Convert back to PIL
            image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=95)
            processed_data = output.getvalue()
            
            logger.info(f"Image preprocessing completed. Original: {len(image_data)} bytes, Processed: {len(processed_data)} bytes")
            return processed_data
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image_data  # Return original if preprocessing fails

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
        """Extract text from image using Google Cloud Vision API with enhanced preprocessing"""
        try:
            if not self.vision_client:
                raise Exception("Vision API client not initialized")
            
            # Read image content
            image_content = image_file.read()
            image_file.seek(0)  # Reset file pointer
            
            # Preprocess image for better OCR
            processed_content = self.preprocess_image_for_ocr(image_content)
            
            # Create Vision API image object
            image = vision.Image(content=processed_content)
            
            # Use document_text_detection for better OCR accuracy
            response = self.vision_client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            
            # Extract text from document with enhanced processing
            all_text = ""
            text_blocks = []
            
            if response.full_text_annotation:
                all_text = response.full_text_annotation.text
                
                # Extract text blocks with positions for better parsing
                for page in response.full_text_annotation.pages:
                    for block in page.blocks:
                        block_text = ""
                        for paragraph in block.paragraphs:
                            para_text = ""
                            for word in paragraph.words:
                                word_text = ''.join([symbol.text for symbol in word.symbols])
                                para_text += word_text + " "
                            block_text += para_text.strip() + "\n"
                        if block_text.strip():
                            text_blocks.append(block_text.strip())
            else:
                # Fallback to regular text detection
                text_response = self.vision_client.text_detection(image=image)
                if text_response.text_annotations:
                    all_text = text_response.text_annotations[0].description
            
            logger.info(f"Extracted text length: {len(all_text)} characters, Text blocks: {len(text_blocks)}")
            return all_text, text_blocks
        
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise

    def extract_cnic_data(self, image_file) -> Dict[str, Any]:
        """Extract structured CNIC data from image with enhanced accuracy"""
        try:
            # Extract raw text with enhanced processing
            raw_text, text_blocks = self.extract_text_from_image(image_file)
            
            # Parse CNIC data from text with multiple strategies
            cnic_data = self._parse_cnic_text_enhanced(raw_text, text_blocks)
            
            return {
                'raw_text': raw_text,
                'parsed_data': cnic_data,
                'text_blocks': text_blocks
            }
        
        except Exception as e:
            logger.error(f"CNIC data extraction failed: {str(e)}")
            raise
    
    def _clean_text(self, text):
        """Clean and normalize the extracted text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        
        # Replace common OCR mistakes
        replacements = {
            'Identily': 'Identity',
            'ldentity': 'Identity',
            'ldenity': 'Identity',
            'Countly': 'Country',
            'Fathel': 'Father',
            'Gendet': 'Gender',
            'Expily': 'Expiry',
            'lssue': 'Issue',
            'Blrth': 'Birth',
            'Blth': 'Birth',
            'Nalional': 'National',
            'Natlonal': 'National',
            'Paklstan': 'Pakistan',
            'PAKLSTAN': 'PAKISTAN',
            'S/o': 'S/O',
            'D/o': 'D/O',
            'W/o': 'W/O'
        }
        
        for mistake, correction in replacements.items():
            text = text.replace(mistake, correction)
            
        return text

    def _parse_cnic_text_enhanced(self, text: str, text_blocks: list) -> Dict[str, Optional[str]]:
        """Enhanced parsing with multiple strategies for CNIC fields"""
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Initialize result
        cnic_data = {
            'identity_number': None,
            'name': None,
            'father_name': None,
            'gender': None,
            'country_of_stay': None,
            'date_of_birth': None,
            'date_of_issue': None,
            'date_of_expiry': None
        }
        
        logger.info(f"Starting enhanced CNIC parsing with {len(text_blocks)} text blocks")
        
        # Strategy 1: Pattern-based extraction
        cnic_data = self._extract_with_patterns(text, cnic_data)
        
        # Strategy 2: Position-based extraction using text blocks
        cnic_data = self._extract_with_positions(text_blocks, cnic_data)
        
        # Strategy 3: Context-based extraction
        cnic_data = self._extract_with_context(text, cnic_data)
        
        # Strategy 4: Fallback extraction for missing fields
        cnic_data = self._fallback_extraction(text, cnic_data)
        
        # Final cleanup and validation
        cnic_data = self._cleanup_extracted_data(cnic_data)
        
        return cnic_data

    def _extract_with_patterns(self, text, result):
        """Extract using enhanced regex patterns"""
        
        logger.info("Applying pattern-based extraction")
        
        # Enhanced CNIC Number patterns
        cnic_patterns = [
            r'(\d{5}[-\s]?\d{7}[-\s]?\d{1})',
            r'(\d{13})',
            r'(?:Identity\s+Number|شناختی\s+نمبر)[:\s]*(\d{5}[-\s]?\d{7}[-\s]?\d{1})',
            r'(?:CNIC|NIC)[:\s]*(\d{5}[-\s]?\d{7}[-\s]?\d{1})',
            r'ID[:\s]*(\d{5}[-\s]?\d{7}[-\s]?\d{1})'
        ]
        
        for pattern in cnic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not result['identity_number']:
                number = re.sub(r'[-\s]', '', match.group(1))
                if len(number) == 13:
                    result['identity_number'] = f"{number[:5]}-{number[5:12]}-{number[12]}"
                    logger.info(f"Found CNIC number: {result['identity_number']}")
                break

        # Enhanced Name patterns
        name_patterns = [
            r'(?:Name|اسم)[:\s]*([A-Za-z\s]{2,40})(?=\s*(?:Father|والد|Gender|جنس|$))',
            r'(?:Holder|Bearer)[:\s]*([A-Za-z\s]{2,40})(?=\s*(?:Father|والد|$))',
            r'(?:^|\n)([A-Z][A-Za-z\s]{2,39})(?=\s*(?:Father|والد|S/O|D/O))',
            r'نام[:\s]*([A-Za-z\s]{2,40})'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match and not result['name']:
                name = match.group(1).strip()
                # Filter out common false positives
                if not re.search(r'PAKISTAN|IDENTITY|CARD|REPUBLIC|GOVERNMENT|NATIONAL|COMPUTERIZED', name, re.IGNORECASE):
                    result['name'] = self._format_name(name)
                    logger.info(f"Found name: {result['name']}")
                    break

        # Enhanced Father's name patterns
        father_patterns = [
            r'(?:Father|والد)[:\s\']*(?:Name)?[:\s]*([A-Za-z\s]{2,40})(?=\s*(?:Gender|جنس|Date|Country|$))',
            r'(?:S/O|D/O|W/O)[:\s]*([A-Za-z\s]{2,40})(?=\s*(?:Gender|Date|Country|$))',
            r'والد\s*کا\s*نام[:\s]*([A-Za-z\s]{2,40})',
            r'Father[\']*s?\s*Name[:\s]*([A-Za-z\s]{2,40})'
        ]
        
        for pattern in father_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not result['father_name']:
                father_name = match.group(1).strip()
                if not re.search(r'PAKISTAN|IDENTITY|CARD|REPUBLIC|GOVERNMENT|NATIONAL', father_name, re.IGNORECASE):
                    result['father_name'] = self._format_name(father_name)
                    logger.info(f"Found father's name: {result['father_name']}")
                    break

        # Enhanced Gender patterns
        gender_patterns = [
            r'(?:Gender|جنس|Sex)[:\s]*(Male|Female|M|F|مرد|عورت)\b',
            r'(?:^|\s)(Male|Female)\s*(?:$|\s)',
            r'(?:Gender|Sex)[:\s]*(MALE|FEMALE)'
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not result['gender']:
                gender_text = match.group(1).upper()
                if gender_text in ['MALE', 'M', 'مرد']:
                    result['gender'] = 'Male'
                elif gender_text in ['FEMALE', 'F', 'عورت']:
                    result['gender'] = 'Female'
                logger.info(f"Found gender: {result['gender']}")
                break

        # Enhanced Country patterns
        country_patterns = [
            r'(?:Country\s+of\s+Stay|Country)[:\s]*([A-Za-z\s]+?)(?=\s*(?:Identity|Date|Gender|$))',
            r'(?:ملک)[:\s]*([A-Za-z\s]+?)(?=\s*(?:شناختی|تاریخ|$))',
            r'(?:Nationality)[:\s]*([A-Za-z\s]+)',
            r'(?:PAKISTAN|Pakistan|پاکستان)'
        ]
        
        for pattern in country_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not result['country_of_stay']:
                if pattern.endswith(')'):  # For PAKISTAN pattern
                    result['country_of_stay'] = 'Pakistan'
                else:
                    country = match.group(1).strip()
                    if country and not re.search(r'IDENTITY|NUMBER|CARD', country, re.IGNORECASE):
                        result['country_of_stay'] = self._format_name(country)
                logger.info(f"Found country: {result['country_of_stay']}")
                break

        # Enhanced Date patterns
        date_patterns = {
            'date_of_birth': [
                r'(?:Date\s+of\s+Birth|Birth|تاریخ\s+پیدائش|DOB)[:\s]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
                r'(?:Born|B)[:\s]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})'
            ],
            'date_of_issue': [
                r'(?:Date\s+of\s+Issue|Issue|تاریخ\s+اجراء|DOI)[:\s]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
                r'(?:Issued|I)[:\s]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})'
            ],
            'date_of_expiry': [
                r'(?:Date\s+of\s+Expiry|Expiry|تاریخ\s+ختم|DOE|Valid\s+Until)[:\s]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
                r'(?:Expires|E)[:\s]*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})'
            ]
        }
        
        for field, patterns in date_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match and not result[field]:
                    result[field] = self._format_date(match.group(1))
                    logger.info(f"Found {field}: {result[field]}")
                    break

        return result

    def _extract_with_positions(self, text_blocks, result):
        """Extract using positional information from text blocks"""
        
        logger.info("Applying position-based extraction")
        
        for i, block in enumerate(text_blocks):
            block_lower = block.lower()
            
            # Look for name patterns in blocks
            if any(keyword in block_lower for keyword in ['name', 'اسم', 'holder']) and not result['name']:
                # Extract name from this or next block
                name_match = re.search(r'(?:name|اسم|holder)[:\s]*([A-Za-z\s]+)', block, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip()
                    if self._is_valid_name(name):
                        result['name'] = self._format_name(name)
                        logger.info(f"Position-based name found: {result['name']}")
                elif i + 1 < len(text_blocks):
                    # Name might be in next block
                    next_block = text_blocks[i + 1].strip()
                    if self._is_valid_name(next_block):
                        result['name'] = self._format_name(next_block)
                        logger.info(f"Position-based name found in next block: {result['name']}")
            
            # Look for father's name
            if any(keyword in block_lower for keyword in ['father', 'والد', 's/o', 'd/o']) and not result['father_name']:
                father_match = re.search(r'(?:father|والد|s/o|d/o)[:\s]*([A-Za-z\s]+)', block, re.IGNORECASE)
                if father_match:
                    father_name = father_match.group(1).strip()
                    if self._is_valid_name(father_name):
                        result['father_name'] = self._format_name(father_name)
                        logger.info(f"Position-based father's name found: {result['father_name']}")
                elif i + 1 < len(text_blocks):
                    next_block = text_blocks[i + 1].strip()
                    if self._is_valid_name(next_block):
                        result['father_name'] = self._format_name(next_block)
                        logger.info(f"Position-based father's name found in next block: {result['father_name']}")

        return result

    def _extract_with_context(self, text, result):
        """Extract using contextual clues and common CNIC layouts"""
        
        logger.info("Applying context-based extraction")
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Name extraction with context
            if 'name' in line_lower and 'father' not in line_lower and not result['name']:
                # Try to extract from same line
                name_match = re.search(r'name[:\s]+([A-Za-z\s]+)', line, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip()
                    if self._is_valid_name(name):
                        result['name'] = self._format_name(name)
                        logger.info(f"Context-based name found: {result['name']}")
                # Try next line
                elif i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if self._is_valid_name(next_line):
                        result['name'] = self._format_name(next_line)
                        logger.info(f"Context-based name found in next line: {result['name']}")
            
            # Father's name extraction
            if 'father' in line_lower and not result['father_name']:
                father_match = re.search(r'father[:\s]+([A-Za-z\s]+)', line, re.IGNORECASE)
                if father_match:
                    father_name = father_match.group(1).strip()
                    if self._is_valid_name(father_name):
                        result['father_name'] = self._format_name(father_name)
                        logger.info(f"Context-based father's name found: {result['father_name']}")
                elif i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if self._is_valid_name(next_line):
                        result['father_name'] = self._format_name(next_line)
                        logger.info(f"Context-based father's name found in next line: {result['father_name']}")

        return result

    def _fallback_extraction(self, text, result):
        """Fallback extraction for missing critical fields"""
        
        logger.info("Applying fallback extraction")
        
        # Extract all dates if any are missing
        date_matches = re.findall(r'(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})', text)
        unique_dates = list(dict.fromkeys(date_matches))  # Remove duplicates while preserving order
        
        date_fields = ['date_of_birth', 'date_of_issue', 'date_of_expiry']
        empty_date_fields = [field for field in date_fields if not result[field]]
        
        for i, field in enumerate(empty_date_fields):
            if i < len(unique_dates):
                result[field] = self._format_date(unique_dates[i])
                logger.info(f"Fallback date extraction for {field}: {result[field]}")
        
        # If name is still missing, try alternative approaches
        if not result['name']:
            # Look for capitalized words that could be names
            words = text.split()
            potential_names = []
            
            for word in words:
                if (word.istitle() and len(word) > 2 and 
                    word.isalpha() and word.lower() not in 
                    ['name', 'father', 'gender', 'country', 'identity', 'date', 'issue', 'birth', 'expiry', 'pakistan', 'card', 'national']):
                    potential_names.append(word)
            
            if potential_names:
                # Take first 2-3 words as potential name
                result['name'] = ' '.join(potential_names[:3])
                logger.info(f"Fallback name extraction: {result['name']}")
        
        # Similar approach for father's name if still missing
        if not result['father_name'] and result['name']:
            # Look for names after the main name in text
            name_words = result['name'].split()
            if name_words:
                text_words = text.split()
                
                # Find position of name in text
                for i, word in enumerate(text_words):
                    if word.lower() == name_words[0].lower():
                        # Look ahead for potential father's name
                        start_pos = i + len(name_words)
                        potential_father_words = []
                        
                        for j in range(start_pos, min(start_pos + 5, len(text_words))):
                            if (j < len(text_words) and text_words[j].istitle() and 
                                text_words[j].isalpha() and len(text_words[j]) > 2):
                                potential_father_words.append(text_words[j])
                            elif potential_father_words:
                                break  # Stop at first non-name word
                        
                        if potential_father_words:
                            result['father_name'] = ' '.join(potential_father_words[:3])
                            logger.info(f"Fallback father's name extraction: {result['father_name']}")
                            break

        return result

    def _is_valid_name(self, name):
        """Check if extracted text is a valid name"""
        if not name or len(name.strip()) < 2:
            return False
        
        # Remove common non-name patterns
        invalid_patterns = [
            r'PAKISTAN|IDENTITY|CARD|REPUBLIC|GOVERNMENT|NATIONAL|COMPUTERIZED',
            r'^\d+$',  # Only numbers
            r'^[^A-Za-z]*$',  # No letters
            r'DATE|BIRTH|ISSUE|EXPIRY|GENDER|COUNTRY'
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return False
        
        # Should contain mostly letters
        letter_count = sum(1 for c in name if c.isalpha())
        return letter_count >= len(name) * 0.7

    def _format_name(self, name):
        """Format name properly"""
        if not name:
            return None
        
        # Clean the name
        name = re.sub(r'[^\w\s]', '', name)  # Remove special characters
        name = re.sub(r'\s+', ' ', name.strip())  # Normalize whitespace
        
        # Title case
        return name.title()

    def _format_date(self, date_str):
        """Format date string consistently"""
        if not date_str:
            return None
        
        # Try different date formats
        from datetime import datetime
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%d/%m/%Y')
            except ValueError:
                continue
        
        return date_str  # Return original if no format matches

    def _cleanup_extracted_data(self, data):
        """Clean up and validate extracted data"""
        for key, value in data.items():
            if value and isinstance(value, str):
                # Remove extra whitespace and clean up
                data[key] = ' '.join(value.split()).strip()
                
                # Remove any remaining artifacts
                if len(data[key]) < 2 or len(data[key]) > 50:
                    data[key] = None
                
                # Specific validations
                if key == 'identity_number' and data[key]:
                    # Ensure CNIC format
                    numbers_only = re.sub(r'[^\d]', '', data[key])
                    if len(numbers_only) == 13:
                        data[key] = f"{numbers_only[:5]}-{numbers_only[5:12]}-{numbers_only[12]}"
                    else:
                        data[key] = None
                
                elif key in ['name', 'father_name'] and data[key]:
                    # Validate names
                    if not self._is_valid_name(data[key]):
                        data[key] = None
        
        return data
