"""
Custom exception handler for Django REST Framework.

This module provides enhanced exception handling for DRF.
"""

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exception: APIException, context: dict) -> Response:
    """
    Custom exception handler for DRF exceptions.
    
    Args:
        exception: The exception that was raised
        context: Dictionary containing request context
        
    Returns:
        Response object or None
    """
    response = exception_handler(exception, context)
    
    if response:
        # Prevent duplicate logging by Django's default request logger
        setattr(response, "_has_been_logged", True)
    
    return response




# Enhanced exception handler specifically for bulk operations
def bulk_operation_exception_handler(exception: APIException, context: dict) -> Response:
    """
    Enhanced exception handler specifically for bulk operations.
    """
    response = exception_handler(exception, context)
    
    if response:
        # Prevent duplicate logging
        setattr(response, "_has_been_logged", True)
    
    return response
