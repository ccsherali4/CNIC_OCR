# Pakistani CNIC OCR - Smart Document Extraction

A powerful web application that uses Google Vision AI to extract information from Pakistani National Identity Cards (CNICs). This application provides both a user-friendly web interface and a RESTful API for automated document processing.

## Features

- **Smart CNIC Recognition**: Extracts all key information from Pakistani CNICs
- **High Accuracy**: Powered by Google Vision AI for reliable text recognition
- **User-Friendly Interface**: Clean, responsive web interface
- **RESTful API**: Easy integration with other applications
- **Multiple Format Support**: JPG, PNG, GIF, BMP, TIFF
- **Real-time Processing**: Fast extraction with confidence scoring
- **Data Export**: Download results as JSON or copy to clipboard

## Extracted Fields

The application extracts the following information from CNIC images using Document OCR:

- **Identity Number** (شناختی نمبر)
- **Name** (اسم)
- **Father's Name** (والد کا نام)
- **Gender** (جنس)
- **Country of Stay**
- **Date of Birth** (تاریخ پیدائش)
- **Date of Issue** (تاریخ اجراء)
- **Date of Expiry** (تاریخ ختم)

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Cloud Account with Vision API enabled
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CNIC_OCR
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv env
   # On Windows
   env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Vision API**
   - Create a Google Cloud Project
   - Enable the Vision API
   - Create a service account and download the JSON key file
   - Place the key file in `credentials/service_account.json`

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## API Usage

### Extract CNIC Data

**Endpoint:** `POST /cnic_ocr`

**Request:**
```bash
curl -X POST \
  http://localhost:5000/cnic_ocr \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@path/to/cnic_image.jpg'
```

**Response:**
```json
{
  "success": true,
  "message": "CNIC data extracted successfully",
  "data": {
    "identity_number": "12345-1234567-1",
    "name": "Muhammad Ali",
    "father_name": "Ahmed Ali",
    "gender": "Male",
    "country_of_stay": "Pakistan",
    "date_of_birth": "01/01/1990",
    "date_of_issue": "01/01/2010",
    "date_of_expiry": "01/01/2030"
  },
  "metadata": {
    "filename": "cnic_image.jpg",
    "confidence_score": 87.5,
    "fields_extracted": 7,
    "total_fields": 8,
    "timestamp": "2024-01-01T12:00:00.000Z",
    "processing_method": "Document OCR"
  },
  "raw_text": "PAKISTAN National Identity Card..."
}
```

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "CNIC OCR API is running",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "version": "1.0.0",
    "status": "healthy"
  }
}
```

## Project Structure

```
CNIC_OCR/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # Project documentation
├── config/
│   └── config.py         # Application configuration
├── services/
│   └── vision_service.py # Google Vision API service
├── utils/
│   ├── validators.py     # Input validation utilities
│   └── response_helpers.py # API response helpers
├── templates/
│   └── index.html        # Web interface template
├── static/
│   ├── css/
│   │   ├── style.css     # Main stylesheet
│   │   └── cnic_styles.css # CNIC-specific styles
│   └── js/
│       └── cnic_app.js   # Frontend JavaScript
└── credentials/
    └── service_account.json # Google Cloud credentials (not in repo)
```

## Configuration

### Environment Variables

- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud service account JSON
- `GEMINI_API_KEY`: Optional Gemini API key for enhanced processing
- `FLASK_DEBUG`: Enable/disable Flask debug mode
- `SECRET_KEY`: Flask secret key for sessions
- `MAX_CONTENT_LENGTH`: Maximum file upload size in bytes

### Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Vision API
4. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Give it the "Cloud Vision API Service Agent" role
   - Generate and download a JSON key
5. Place the JSON key in `credentials/service_account.json`

## Usage Tips

### For Best Results

- Ensure the CNIC image is well-lit and clear
- Avoid shadows or glare on the card
- Make sure all text is visible and legible
- Use high-resolution images when possible
- Keep the card flat and properly aligned

### Common Issues

- **Low confidence scores**: Try improving image quality
- **Missing fields**: Ensure all parts of the CNIC are visible
- **API errors**: Check your Google Cloud credentials and API quotas

## API Integration Examples

### Python
```python
import requests

url = "http://localhost:5000/cnic_ocr"
files = {"image": open("cnic_image.jpg", "rb")}
response = requests.post(url, files=files)
data = response.json()
print(data["data"]["name"])
```

### JavaScript
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('/cnic_ocr', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Name:', data.data.name);
    console.log('CNIC:', data.data.identity_number);
});
```

### cURL
```bash
curl -X POST \
  http://localhost:5000/cnic_ocr \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@cnic_front.jpg'
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Include sample images (with sensitive information removed)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Note

This application processes sensitive identity documents. In production:
- Use HTTPS encryption
- Implement proper authentication
- Log access attempts
- Consider data retention policies
- Ensure compliance with privacy regulations API

A Flask-based REST API for extracting text and structured data from Pakistani CNIC (Computerized National Identity Card) images using Google Cloud Vision API.

## 🚀 Features

- **🔍 High-Accuracy OCR**: Extract text from CNIC images using Google Cloud Vision API
- **📋 Structured Data Parsing**: Automatically parse CNIC fields (name, father's name, dates, etc.)
- **🎨 Beautiful Web Interface**: Modern, responsive web UI with drag & drop functionality
- **🌐 RESTful API**: Clean API endpoints for integration
- **🔒 Secure**: Proper input validation and error handling
- **📱 Multi-format Support**: PNG, JPG, JPEG, GIF, BMP, TIFF

## 📁 Project Structure

```
CNIC_OCR/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                # Documentation
├── .gitignore               # Git ignore rules
├── config/
│   └── config.py            # Configuration settings
├── services/
│   └── vision_service.py    # Google Vision API service
├── utils/
│   ├── validators.py        # Input validation utilities
│   └── response_helpers.py  # API response helpers
├── templates/
│   └── index.html           # Web interface template
└── static/
    ├── css/
    │   └── style.css        # Styles
    └── js/
        └── app.js           # JavaScript functionality
```

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ccsherali4/CNIC_OCR.git
cd CNIC_OCR
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Google Cloud Vision API

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Vision API

2. **Create Service Account:**
   - Go to IAM & Admin > Service Accounts
   - Create a new service account
   - Download the JSON credentials file

3. **Add Credentials:**
   - Create a `credentials` folder in the project root
   - Place your `service_account.json` file in the `credentials` folder

### 5. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 🌐 API Endpoints

### Web Interface
```
GET /
```
Access the beautiful web interface for uploading and processing images.

### Health Check
```
GET /health
```
Returns API status and configuration information.

### Test Vision API
```
GET /test-vision
```
Tests the Google Cloud Vision API configuration.

### Extract Text from Image
```
POST /api/extract-text
```
**Request:** Form data with `image` file
**Response:** JSON with extracted text and structured data

**Example:**
```bash
curl -X POST -F "image=@cnic_image.jpg" http://localhost:5000/api/extract-text
```

### API Status
```
GET /api/status
```
Returns detailed status of all system components.

## 📋 Response Format

**Success Response:**
```json
{
  "success": true,
  "message": "Text extracted successfully",
  "data": {
    "extracted_text": "Full text from image...",
    "structured_data": {
      "cnic_number": "12345-1234567-1",
      "name": "JOHN DOE",
      "father_name": "FATHER NAME",
      "date_of_birth": "01/01/1990",
      "date_of_issue": "01/01/2020",
      "date_of_expiry": "01/01/2030",
      "gender": "Male"
    },
    "filename": "cnic_image.jpg",
    "timestamp": "2025-08-17T12:00:00.000Z"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error description"
}
```

## 🎯 Use Cases

- **Identity Verification Systems**
- **KYC (Know Your Customer) Applications**
- **Document Digitization**
- **Government Services**
- **Banking and Financial Services**
- **Insurance Applications**

## 🔧 Configuration

The application can be configured through environment variables:

```env
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
GOOGLE_APPLICATION_CREDENTIALS=credentials/service_account.json
MAX_CONTENT_LENGTH=16777216
```

## 📱 Supported File Formats

- PNG
- JPG/JPEG
- GIF
- BMP
- TIFF
- Maximum file size: 16MB

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Production Considerations
- Use a production WSGI server (Gunicorn, uWSGI)
- Set up proper logging and monitoring
- Implement rate limiting
- Use environment variables for sensitive configuration
- Set up SSL/TLS certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Cloud Vision API for text extraction
- Flask for the web framework
- All contributors and users of this project

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Made with ❤️ for document digitization and identity verification.
