"""
Logging utilities for django-bulk-drf.

This module provides enhanced logging capabilities that work around
Django REST Framework's log suppression issues.
"""

import logging
import sys
from typing import Optional
from django.conf import settings

from .config import get_bulk_drf_settings


def setup_bulk_drf_logging():
    """
    Setup enhanced logging for django-bulk-drf.
    
    This function should be called explicitly by users who want to enable
    django-bulk-drf logging. By default, the package uses NullHandler
    to prevent unwanted log output.
    
    Example usage in Django settings.py:
        from django_bulk_drf.logging_utils import setup_bulk_drf_logging
        setup_bulk_drf_logging()
    
    Or configure via Django's LOGGING setting for more control.
    """
    bulk_settings = get_bulk_drf_settings()
    
    # Get the django-bulk-drf logger
    logger = logging.getLogger('django_bulk_drf')
    
    # Remove the default NullHandler
    logger.handlers.clear()
    
    # Configure formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add stdout handler if force_stdout_logging is enabled
    if bulk_settings.get('force_stdout_logging', False):
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)
    
    # Add file handler if log_to_file is enabled
    if bulk_settings.get('log_to_file', False):
        log_file_path = bulk_settings.get('log_file_path', 'django_bulk_drf.log')
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # If no handlers were added, add a console handler so logs appear
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Set log level
    log_level = bulk_settings.get('log_level', 'WARNING').upper()
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    logger.setLevel(level_map.get(log_level, logging.WARNING))
    
    # Enable debug logging if requested
    if bulk_settings.get('enable_debug_logging', False):
        logger.setLevel(logging.DEBUG)
    
    # Ensure logs propagate to parent loggers
    logger.propagate = True
    
    logger.debug("django-bulk-drf logging configured successfully")
    return logger


def get_bulk_drf_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for django-bulk-drf components.
    
    Args:
        name: Optional logger name. If None, uses 'django_bulk_drf'
        
    Returns:
        Configured logger instance
    """
    if name is None:
        name = 'django_bulk_drf'
    elif not name.startswith('django_bulk_drf'):
        name = f'django_bulk_drf.{name}'
    
    return logging.getLogger(name)


def log_with_force_print(message: str, level: str = 'INFO', logger_name: str = 'django_bulk_drf'):
    """
    Log a message with forced output to stdout.
    
    This function ensures the message is visible even when DRF suppresses logs.
    
    Args:
        message: The message to log
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        logger_name: Name of the logger to use
    """
    logger = get_bulk_drf_logger(logger_name)
    
    # Log normally
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message)
    
    # Also print to stdout as a fallback
    print(f"[{level.upper()}] {logger_name}: {message}", file=sys.stdout, flush=True)


def log_bulk_operation_start(operation_type: str, item_count: int, **kwargs):
    """
    Log the start of a bulk operation.
    
    Args:
        operation_type: Type of operation ('create', 'update', 'upsert', 'delete')
        item_count: Number of items being processed
        **kwargs: Additional context information
    """
    logger = get_bulk_drf_logger('bulk_operations')
    
    context_info = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    message = f"Starting {operation_type} operation with {item_count} items"
    if context_info:
        message += f" ({context_info})"
    
    logger.debug(message)
    
    # Force print for visibility
    print(f"[BULK-OP] {message}", file=sys.stdout, flush=True)


def log_bulk_operation_progress(current: int, total: int, operation_type: str = "operation"):
    """
    Log progress of a bulk operation.
    
    Args:
        current: Current progress count
        total: Total items to process
        operation_type: Type of operation being performed
    """
    logger = get_bulk_drf_logger('bulk_operations')
    
    percentage = (current / total * 100) if total > 0 else 0
    message = f"{operation_type} progress: {current}/{total} ({percentage:.1f}%)"
    
    logger.debug(message)
    
    # Print progress every 10% or at completion
    if current % max(1, total // 10) == 0 or current == total:
        print(f"[PROGRESS] {message}", file=sys.stdout, flush=True)


def log_bulk_operation_complete(operation_type: str, success_count: int, error_count: int, **kwargs):
    """
    Log the completion of a bulk operation.
    
    Args:
        operation_type: Type of operation that completed
        success_count: Number of successful operations
        error_count: Number of failed operations
        **kwargs: Additional context information
    """
    logger = get_bulk_drf_logger('bulk_operations')
    
    context_info = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    message = f"Completed {operation_type} operation: {success_count} success, {error_count} errors"
    if context_info:
        message += f" ({context_info})"
    
    if error_count > 0:
        logger.warning(message)
    else:
        logger.debug(message)
    
    # Force print for visibility
    print(f"[BULK-COMPLETE] {message}", file=sys.stdout, flush=True)


def log_api_request(method: str, path: str, status_code: int, duration: float, **kwargs):
    """
    Log API request details.
    
    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration: Request duration in seconds
        **kwargs: Additional context information
    """
    logger = get_bulk_drf_logger('api_requests')
    
    context_info = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    message = f"{method} {path} -> {status_code} ({duration:.3f}s)"
    if context_info:
        message += f" ({context_info})"
    
    if status_code >= 400:
        logger.warning(message)
    else:
        logger.debug(message)
    
    # Force print for errors
    if status_code >= 400:
        print(f"[API-ERROR] {message}", file=sys.stdout, flush=True)


def log_celery_task_start(task_name: str, task_id: str, **kwargs):
    """
    Log the start of a Celery task.
    
    Args:
        task_name: Name of the Celery task
        task_id: Celery task ID
        **kwargs: Additional context information
    """
    logger = get_bulk_drf_logger('celery_tasks')
    
    context_info = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    message = f"Starting Celery task {task_name} (ID: {task_id})"
    if context_info:
        message += f" ({context_info})"
    
    logger.debug(message)
    print(f"[CELERY-START] {message}", file=sys.stdout, flush=True)


def log_celery_task_complete(task_name: str, task_id: str, success: bool, **kwargs):
    """
    Log the completion of a Celery task.
    
    Args:
        task_name: Name of the Celery task
        task_id: Celery task ID
        success: Whether the task completed successfully
        **kwargs: Additional context information
    """
    logger = get_bulk_drf_logger('celery_tasks')
    
    context_info = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    status = "SUCCESS" if success else "FAILED"
    message = f"Celery task {task_name} {status} (ID: {task_id})"
    if context_info:
        message += f" ({context_info})"
    
    if success:
        logger.debug(message)
    else:
        logger.error(message)
    
    print(f"[CELERY-{status}] {message}", file=sys.stdout, flush=True)


class LoggingContext:
    """
    Context manager for enhanced logging with automatic cleanup.
    """
    
    def __init__(self, operation_name: str, logger_name: str = 'django_bulk_drf'):
        self.operation_name = operation_name
        self.logger = get_bulk_drf_logger(logger_name)
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting {self.operation_name}")
        print(f"[START] {self.operation_name}", file=sys.stdout, flush=True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is None:
            self.logger.debug(f"Completed {self.operation_name} ({duration:.3f}s)")
            print(f"[COMPLETE] {self.operation_name} ({duration:.3f}s)", file=sys.stdout, flush=True)
        else:
            self.logger.error(f"Failed {self.operation_name} ({duration:.3f}s): {exc_val}")
            print(f"[FAILED] {self.operation_name} ({duration:.3f}s): {exc_val}", file=sys.stdout, flush=True)
        
        return False  # Don't suppress exceptions
