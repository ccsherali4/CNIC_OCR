// CNIC OCR Application JavaScript
class CNICOCRApp {
    constructor() {
        this.currentFile = null;
        this.extractedData = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File input change
        document.getElementById('imageInput').addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Drag and drop
        const uploadSection = document.getElementById('uploadSection');
        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.classList.add('drag-over');
        });

        uploadSection.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('drag-over');
        });

        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });

        // Button event listeners
        document.getElementById('extractBtn').addEventListener('click', () => {
            this.extractCNICData();
        });

        document.getElementById('changeImageBtn').addEventListener('click', () => {
            this.resetToUpload();
        });

        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.downloadData();
        });

        document.getElementById('copyBtn').addEventListener('click', () => {
            this.copyDataToClipboard();
        });

        document.getElementById('newExtractionBtn').addEventListener('click', () => {
            this.resetToUpload();
        });

        document.getElementById('retryBtn').addEventListener('click', () => {
            this.showPreview();
        });

        document.getElementById('toggleRawTextBtn').addEventListener('click', () => {
            this.toggleRawText();
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Please select a valid image file (JPG, PNG, GIF, BMP, TIFF)');
            return;
        }

        // Validate file size (16MB max)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            this.showError('File size too large. Please select an image smaller than 16MB.');
            return;
        }

        this.currentFile = file;
        this.showPreview();
    }

    showPreview() {
        if (!this.currentFile) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('previewImage').src = e.target.result;
            this.hideAllSections();
            document.getElementById('previewSection').style.display = 'block';
        };
        reader.readAsDataURL(this.currentFile);
    }

    async extractCNICData() {
        if (!this.currentFile) {
            this.showError('Please select a CNIC image first.');
            return;
        }

        this.showLoading();

        const formData = new FormData();
        formData.append('image', this.currentFile);

        try {
            const response = await fetch('/cnic_ocr', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.extractedData = result;
                this.displayResults(result);
            } else {
                this.showError(result.message || 'Failed to extract CNIC data');
            }
        } catch (error) {
            console.error('Extraction error:', error);
            this.showError('Network error occurred. Please check your connection and try again.');
        }
    }

    displayResults(result) {
        const data = result.data;
        const metadata = result.metadata;

        // Update confidence score
        const confidenceScore = metadata.confidence_score || 0;
        document.getElementById('confidenceScore').textContent = `${confidenceScore}%`;
        
        const confidenceBadge = document.getElementById('confidenceBadge');
        confidenceBadge.className = 'confidence-badge';
        if (confidenceScore >= 80) {
            confidenceBadge.classList.add('high');
        } else if (confidenceScore >= 60) {
            confidenceBadge.classList.add('medium');
        } else {
            confidenceBadge.classList.add('low');
        }

        // Update CNIC fields
        this.updateField('identityNumber', data.identity_number);
        this.updateField('name', data.name);
        this.updateField('fatherName', data.father_name);
        this.updateField('gender', data.gender);
        this.updateField('countryOfStay', data.country_of_stay);
        this.updateField('dateOfBirth', data.date_of_birth);
        this.updateField('dateOfIssue', data.date_of_issue);
        this.updateField('dateOfExpiry', data.date_of_expiry);

        // Update raw text
        document.getElementById('rawText').textContent = result.raw_text || 'No raw text available';

        this.hideAllSections();
        document.getElementById('resultsSection').style.display = 'block';
    }

    updateField(fieldId, value) {
        const fieldElement = document.getElementById(fieldId);
        const fieldContainer = fieldElement.closest('.data-field');
        
        if (value && value !== null && value !== '') {
            fieldElement.textContent = value;
            fieldContainer.classList.remove('empty');
            fieldContainer.classList.add('filled');
        } else {
            fieldElement.textContent = '-';
            fieldContainer.classList.remove('filled');
            fieldContainer.classList.add('empty');
        }
    }

    showLoading() {
        this.hideAllSections();
        document.getElementById('loadingSection').style.display = 'block';
    }

    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        this.hideAllSections();
        document.getElementById('errorSection').style.display = 'block';
    }

    hideAllSections() {
        const sections = ['uploadSection', 'previewSection', 'loadingSection', 'resultsSection', 'errorSection'];
        sections.forEach(sectionId => {
            document.getElementById(sectionId).style.display = 'none';
        });
    }

    resetToUpload() {
        this.currentFile = null;
        this.extractedData = null;
        document.getElementById('imageInput').value = '';
        this.hideAllSections();
        document.getElementById('uploadSection').style.display = 'block';
    }

    downloadData() {
        if (!this.extractedData) return;

        const dataToDownload = {
            cnic_data: this.extractedData.data,
            metadata: this.extractedData.metadata,
            extracted_at: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(dataToDownload, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cnic_data_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('Data downloaded successfully!', 'success');
    }

    async copyDataToClipboard() {
        if (!this.extractedData) return;

        const dataText = JSON.stringify(this.extractedData.data, null, 2);
        
        try {
            await navigator.clipboard.writeText(dataText);
            this.showNotification('CNIC data copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy to clipboard:', err);
            this.showNotification('Failed to copy data. Please try again.', 'error');
        }
    }

    toggleRawText() {
        const rawTextContent = document.getElementById('rawTextContent');
        const toggleBtn = document.getElementById('toggleRawTextBtn');
        
        if (rawTextContent.style.display === 'none') {
            rawTextContent.style.display = 'block';
            toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Hide Raw Extracted Text';
        } else {
            rawTextContent.style.display = 'none';
            toggleBtn.innerHTML = '<i class="fas fa-eye"></i> Show Raw Extracted Text';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check' : type === 'error' ? 'fa-times' : 'fa-info'}"></i>
            <span>${message}</span>
        `;

        // Add to document
        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CNICOCRApp();
});

// Add CSS for notifications
const notificationCSS = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 10px;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.notification.show {
    transform: translateX(0);
}

.notification.success {
    background-color: #28a745;
}

.notification.error {
    background-color: #dc3545;
}

.notification.info {
    background-color: #17a2b8;
}
`;

const style = document.createElement('style');
style.textContent = notificationCSS;
document.head.appendChild(style);
