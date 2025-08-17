# 🔑 Getting Your Gemini API Key

To use the text extraction features, you need a Google Gemini API key.

## Step 1: Get Gemini API Key

1. **Visit Google AI Studio:**
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key:**
   - Click "Create API Key"
   - Select your project or create a new one
   - Copy the generated API key

3. **Add to Environment:**
   - Open the `.env` file in your project
   - Uncomment the line: `# GEMINI_API_KEY=your-gemini-api-key-here`
   - Replace `your-gemini-api-key-here` with your actual API key
   - Save the file

## Step 2: Test the Setup

1. **Start the Web Application:**
   ```bash
   venv\Scripts\python.exe web_app.py
   ```

2. **Test Gemini Connection:**
   - Open browser: http://localhost:5000/test-gemini
   - Should show successful response with world capitals

3. **Use the Web Interface:**
   - Open: http://localhost:5000
   - Upload an image and extract text

## Example .env File

```env
# Flask settings
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production

# Google Cloud settings
GOOGLE_APPLICATION_CREDENTIALS=credentials/service_account.json

# Gemini API key (Required for text extraction)
GEMINI_API_KEY=AIzaSyD... (your actual key here)

# Upload settings
MAX_CONTENT_LENGTH=16777216
```

## 🎯 Features Available

1. **Beautiful Web Interface** - Modern, responsive design
2. **Drag & Drop Upload** - Easy image uploading
3. **Gemini AI Processing** - Most accurate text extraction
4. **Structured Data** - Automatically parse ID cards/documents
5. **Text Statistics** - Character, word, and line counts
6. **Copy & Download** - Easy text management
7. **Error Handling** - Graceful error messages

## 🚀 Quick Start

Once you have your API key configured:

1. Start the server:
   ```bash
   venv\Scripts\python.exe web_app.py
   ```

2. Open your browser: http://localhost:5000

3. Upload any image with text and watch the magic happen!

## 📋 API Endpoints

- `GET /` - Beautiful web interface
- `GET /test-gemini` - Test Gemini API connection
- `POST /api/extract-text` - Extract text from images
- `GET /api/status` - Check system status

Your CNIC OCR application is now ready with the most advanced AI-powered text extraction!
