// DOM Elements
const uploadSection = document.getElementById('uploadSection');
const previewSection = document.getElementById('previewSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

const imageInput = document.getElementById('imageInput');
const previewImage = document.getElementById('previewImage');
const extractBtn = document.getElementById('extractBtn');
const changeImageBtn = document.getElementById('changeImageBtn');
const copyBtn = document.getElementById('copyBtn');
const downloadBtn = document.getElementById('downloadBtn');
const newImageBtn = document.getElementById('newImageBtn');
const retryBtn = document.getElementById('retryBtn');

const extractedText = document.getElementById('extractedText');
const structuredData = document.getElementById('structuredData');
const dataGrid = document.getElementById('dataGrid');
const charCount = document.getElementById('charCount');
const wordCount = document.getElementById('wordCount');
const lineCount = document.getElementById('lineCount');
const errorMessage = document.getElementById('errorMessage');

let currentFile = null;
let extractedTextContent = '';

// Event Listeners
imageInput.addEventListener('change', handleImageSelect);
extractBtn.addEventListener('click', extractText);
changeImageBtn.addEventListener('click', resetToUpload);
copyBtn.addEventListener('click', copyTextToClipboard);
downloadBtn.addEventListener('click', downloadResults);
newImageBtn.addEventListener('click', resetToUpload);
retryBtn.addEventListener('click', extractText);

// Drag and drop functionality
const uploadCard = document.querySelector('.upload-card');
uploadCard.addEventListener('dragover', handleDragOver);
uploadCard.addEventListener('drop', handleDrop);
uploadCard.addEventListener('dragleave', handleDragLeave);

function handleDragOver(e) {
    e.preventDefault();
    uploadCard.style.borderColor = '#667eea';
    uploadCard.style.backgroundColor = 'rgba(102, 126, 234, 0.05)';
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadCard.style.borderColor = '';
    uploadCard.style.backgroundColor = '';
}

function handleDrop(e) {
    e.preventDefault();
    uploadCard.style.borderColor = '';
    uploadCard.style.backgroundColor = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (isValidImageFile(file)) {
            currentFile = file;
            displayPreview(file);
        } else {
            showError('Please select a valid image file (JPG, PNG, GIF, BMP, TIFF)');
        }
    }
}

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (file) {
        if (isValidImageFile(file)) {
            currentFile = file;
            displayPreview(file);
        } else {
            showError('Please select a valid image file (JPG, PNG, GIF, BMP, TIFF)');
        }
    }
}

function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    if (!validTypes.includes(file.type)) {
        return false;
    }
    
    if (file.size > maxSize) {
        showError('File size must be less than 16MB');
        return false;
    }
    
    return true;
}

function displayPreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        showSection('preview');
    };
    reader.readAsDataURL(file);
}

async function extractText() {
    if (!currentFile) {
        showError('Please select an image first');
        return;
    }
    
    showSection('loading');
    
    const formData = new FormData();
    formData.append('image', currentFile);
    
    try {
        const response = await fetch('/api/extract-text', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.data);
        } else {
            showError(result.message || 'Failed to extract text from image');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
    }
}

function displayResults(data) {
    extractedTextContent = data.extracted_text || '';
    extractedText.textContent = extractedTextContent;
    
    // Update text statistics
    const chars = extractedTextContent.length;
    const words = extractedTextContent.trim() ? extractedTextContent.trim().split(/\s+/).length : 0;
    const lines = extractedTextContent.split('\n').length;
    
    charCount.textContent = chars.toLocaleString();
    wordCount.textContent = words.toLocaleString();
    lineCount.textContent = lines.toLocaleString();
    
    // Show structured data if available
    if (data.structured_data && Object.keys(data.structured_data).length > 0) {
        displayStructuredData(data.structured_data);
        structuredData.style.display = 'block';
    } else {
        structuredData.style.display = 'none';
    }
    
    showSection('results');
}

function displayStructuredData(data) {
    dataGrid.innerHTML = '';
    
    for (const [key, value] of Object.entries(data)) {
        if (value && value.trim()) {
            const dataItem = document.createElement('div');
            dataItem.className = 'data-item';
            
            const label = document.createElement('div');
            label.className = 'data-label';
            label.textContent = formatLabel(key);
            
            const valueDiv = document.createElement('div');
            valueDiv.className = 'data-value';
            valueDiv.textContent = value;
            
            dataItem.appendChild(label);
            dataItem.appendChild(valueDiv);
            dataGrid.appendChild(dataItem);
        }
    }
}

function formatLabel(key) {
    return key.replace(/_/g, ' ')
              .replace(/\b\w/g, l => l.toUpperCase());
}

function copyTextToClipboard() {
    if (extractedTextContent) {
        navigator.clipboard.writeText(extractedTextContent).then(() => {
            // Show success feedback
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            copyBtn.style.background = '#28a745';
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.style.background = '';
            }, 2000);
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = extractedTextContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            copyBtn.style.background = '#28a745';
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.style.background = '';
            }, 2000);
        });
    }
}

function downloadResults() {
    if (!extractedTextContent) return;
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const filename = `extracted_text_${timestamp}.txt`;
    
    const blob = new Blob([extractedTextContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    // Show success feedback
    const originalText = downloadBtn.innerHTML;
    downloadBtn.innerHTML = '<i class="fas fa-check"></i> Downloaded!';
    downloadBtn.style.background = '#28a745';
    
    setTimeout(() => {
        downloadBtn.innerHTML = originalText;
        downloadBtn.style.background = '';
    }, 2000);
}

function resetToUpload() {
    currentFile = null;
    extractedTextContent = '';
    imageInput.value = '';
    previewImage.src = '';
    extractedText.textContent = '';
    dataGrid.innerHTML = '';
    showSection('upload');
}

function showSection(section) {
    // Hide all sections
    uploadSection.style.display = 'none';
    previewSection.style.display = 'none';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Show the requested section
    switch (section) {
        case 'upload':
            uploadSection.style.display = 'block';
            break;
        case 'preview':
            previewSection.style.display = 'block';
            break;
        case 'loading':
            loadingSection.style.display = 'block';
            break;
        case 'results':
            resultsSection.style.display = 'block';
            break;
        case 'error':
            errorSection.style.display = 'block';
            break;
    }
}

function showError(message) {
    errorMessage.textContent = message;
    showSection('error');
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('CNIC OCR Web App initialized');
    showSection('upload');
});
