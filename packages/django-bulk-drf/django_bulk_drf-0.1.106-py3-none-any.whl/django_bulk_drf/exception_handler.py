"""
Custom exception handler for Django REST Framework.

This module provides enhanced exception handling and logging for DRF,
addressing the issue where logs are suppressed unless using print(stderr).

Based on the approach from: https://www.untangled.dev/2023/07/22/django-drf-exception-logging/
"""

import logging
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

import logging

logger = logging.getLogger('django_bulk_drf.exception_handler')


def custom_exception_handler(exception: APIException, context: dict) -> Response:
    """
    Custom exception handler that provides enhanced logging for DRF exceptions.
    
    This handler logs detailed information about API exceptions while preventing
    duplicate logging from Django's default request logger.
    
    Args:
        exception: The exception that was raised
        context: Dictionary containing request context
        
    Returns:
        Response object or None
    """
    response = exception_handler(exception, context)
    
    if response:
        request = context.get('request')
        path = request.path if request else 'unknown'
        
        # Log different types of exceptions with appropriate detail
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            _log_bad_request(request, response, exception)
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            _log_unauthorized(request, response, exception)
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            _log_forbidden(request, response, exception)
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            _log_not_found(request, response, exception)
        elif response.status_code >= 500:
            _log_server_error(request, response, exception)
        
        # Prevent duplicate logging by Django's default request logger
        setattr(response, "_has_been_logged", True)
    
    return response


def _log_bad_request(request, response, exception):
    """Log 400 Bad Request exceptions with detailed context."""
    try:
        # Extract request data safely
        request_data = {}
        if hasattr(request, 'data') and request.data:
            # Limit the size of logged data to avoid performance issues
            request_data = _limit_data_size(request.data, max_size=1000)
        
        # Extract validation errors if available
        validation_errors = {}
        if hasattr(response, 'data') and response.data:
            validation_errors = _limit_data_size(response.data, max_size=1000)
        
        logger.warning(
            "Bad Request: %s",
            request.path,
            extra={
                'status_code': response.status_code,
                'http_method': request.method,
                'request_data': request_data,
                'validation_errors': validation_errors,
                'exception_type': type(exception).__name__,
                'user': getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'unknown',
            }
        )
        
        # Also log to stdout for immediate visibility
        print(f"[BAD-REQUEST] {request.method} {request.path} - Validation errors: {validation_errors}", 
              flush=True)
        
    except Exception as e:
        logger.error(f"Error logging bad request: {e}")


def _log_unauthorized(request, response, exception):
    """Log 401 Unauthorized exceptions."""
    logger.warning(
        "Unauthorized: %s",
        request.path,
        extra={
            'status_code': response.status_code,
            'http_method': request.method,
            'exception_type': type(exception).__name__,
            'user': getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'unknown',
        }
    )


def _log_forbidden(request, response, exception):
    """Log 403 Forbidden exceptions."""
    logger.warning(
        "Forbidden: %s",
        request.path,
        extra={
            'status_code': response.status_code,
            'http_method': request.method,
            'exception_type': type(exception).__name__,
            'user': getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'unknown',
        }
    )


def _log_not_found(request, response, exception):
    """Log 404 Not Found exceptions."""
    logger.debug(
        "Not Found: %s",
        request.path,
        extra={
            'status_code': response.status_code,
            'http_method': request.method,
            'exception_type': type(exception).__name__,
        }
    )


def _log_server_error(request, response, exception):
    """Log 5xx Server Error exceptions."""
    logger.error(
        "Server Error: %s",
        request.path,
        extra={
            'status_code': response.status_code,
            'http_method': request.method,
            'exception_type': type(exception).__name__,
            'user': getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'unknown',
        }
    )


def _limit_data_size(data, max_size=1000):
    """
    Limit the size of data being logged to prevent performance issues.
    
    Args:
        data: The data to limit
        max_size: Maximum size in characters
        
    Returns:
        Limited data or truncated version
    """
    try:
        import json
        data_str = json.dumps(data) if not isinstance(data, str) else data
        
        if len(data_str) > max_size:
            return data_str[:max_size] + "... (truncated)"
        
        return data
    except Exception:
        return str(data)[:max_size] + "..." if len(str(data)) > max_size else str(data)


# Enhanced exception handler specifically for bulk operations
def bulk_operation_exception_handler(exception: APIException, context: dict) -> Response:
    """
    Enhanced exception handler specifically for bulk operations.
    
    This handler provides detailed logging for bulk operation failures
    and includes progress information when available.
    """
    response = exception_handler(exception, context)
    
    if response:
        request = context.get('request')
        
        # Check if this is a bulk operation
        is_bulk_operation = (
            isinstance(getattr(request, 'data', None), list) or
            'bulk' in request.path.lower() or
            'unique_fields' in request.GET
        )
        
        if is_bulk_operation:
            _log_bulk_operation_error(request, response, exception)
        
        # Prevent duplicate logging
        setattr(response, "_has_been_logged", True)
    
    return response


def _log_bulk_operation_error(request, response, exception):
    """Log bulk operation specific errors with enhanced context."""
    try:
        # Extract bulk operation context
        unique_fields = request.GET.get('unique_fields', '')
        update_fields = request.GET.get('update_fields', '')
        max_items = request.GET.get('max_items', '')
        
        # Count items being processed
        item_count = 0
        if hasattr(request, 'data') and isinstance(request.data, list):
            item_count = len(request.data)
        
        logger.error(
            "Bulk Operation Error: %s",
            request.path,
            extra={
                'status_code': response.status_code,
                'http_method': request.method,
                'operation_type': 'bulk_operation',
                'item_count': item_count,
                'unique_fields': unique_fields,
                'update_fields': update_fields,
                'max_items': max_items,
                'exception_type': type(exception).__name__,
                'user': getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'unknown',
            }
        )
        
        # Force print for immediate visibility
        print(f"[BULK-ERROR] {request.method} {request.path} - {item_count} items - {type(exception).__name__}: {str(exception)}", 
              flush=True)
        
    except Exception as e:
        logger.error(f"Error logging bulk operation error: {e}")
