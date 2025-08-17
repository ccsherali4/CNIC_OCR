from flask import jsonify
from typing import Any, Dict

def success_response(data: Any, message: str = "Success", status_code: int = 200) -> tuple:
    """Create a standardized success response"""
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code

def error_response(message: str, status_code: int = 400, error_code: str = None) -> tuple:
    """Create a standardized error response"""
    response = {
        'success': False,
        'message': message,
        'error_code': error_code
    }
    return jsonify(response), status_code

def validation_error_response(errors: Dict[str, str]) -> tuple:
    """Create a validation error response"""
    response = {
        'success': False,
        'message': 'Validation failed',
        'errors': errors
    }
    return jsonify(response), 400
