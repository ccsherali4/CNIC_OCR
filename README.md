# CNIC OCR API

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
