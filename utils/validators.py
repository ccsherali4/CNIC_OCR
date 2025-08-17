from werkzeug.datastructures import FileStorage
import os

def validate_image_file(file: FileStorage) -> bool:
    """Validate if the uploaded file is a valid image"""
    if not file or not file.filename:
        return False
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    return file_extension in allowed_extensions

def validate_file_size(file: FileStorage, max_size_mb: int = 16) -> bool:
    """Validate file size"""
    if not file:
        return False
    
    # Get file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes
