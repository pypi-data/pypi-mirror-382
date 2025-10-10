"""
Configuration validation and settings for django-bulk-drf.

This module provides clean, modern settings without backwards compatibility.
All settings use the BULK_DRF_ prefix for consistency and clarity.
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def validate_bulk_drf_config():
    """
    Validate that required settings are configured for django-bulk-drf.

    Raises:
        ImproperlyConfigured: If required settings are missing or invalid
    """
    # Check if cache is configured
    if not hasattr(settings, "CACHES") or "default" not in settings.CACHES:
        raise ImproperlyConfigured(
            "django-bulk-drf requires a cache backend to be configured. "
            "Please add CACHES setting to your Django settings."
        )

    # Check if Celery is configured
    if not hasattr(settings, "CELERY_BROKER_URL"):
        raise ImproperlyConfigured(
            "django-bulk-drf requires Celery to be configured. "
            "Please add CELERY_BROKER_URL setting to your Django settings."
        )

    # Check if REST framework is installed
    if "rest_framework" not in getattr(settings, "INSTALLED_APPS", []):
        raise ImproperlyConfigured(
            "django-bulk-drf requires Django REST Framework to be installed. "
            "Please add 'rest_framework' to INSTALLED_APPS."
        )


def get_bulk_drf_settings():
    """
    Get django-bulk-drf specific settings with defaults.

    Settings can be overridden in Django settings using BULK_DRF_* prefix.

    Returns:
        dict: Settings dictionary with defaults applied
    """
    return {
        "chunk_size": getattr(settings, "BULK_DRF_CHUNK_SIZE", 100),
        "max_records": getattr(settings, "BULK_DRF_MAX_RECORDS", 10000),
        "cache_timeout": getattr(settings, "BULK_DRF_CACHE_TIMEOUT", 86400),
        "progress_update_interval": getattr(
            settings, "BULK_DRF_PROGRESS_UPDATE_INTERVAL", 10
        ),
        "batch_size": getattr(settings, "BULK_DRF_BATCH_SIZE", 1000),
        "use_optimized_tasks": getattr(settings, "BULK_DRF_USE_OPTIMIZED_TASKS", True),
        "auto_optimize_queries": getattr(
            settings, "BULK_DRF_AUTO_OPTIMIZE_QUERIES", True
        ),
        "query_timeout": getattr(settings, "BULK_DRF_QUERY_TIMEOUT", 300),  # 5 minutes
        "enable_metrics": getattr(settings, "BULK_DRF_ENABLE_METRICS", False),
        # Sync Upsert Settings
        "sync_upsert_max_items": getattr(
            settings, "BULK_DRF_SYNC_UPSERT_MAX_ITEMS", 50
        ),
        "sync_upsert_batch_size": getattr(
            settings, "BULK_DRF_SYNC_UPSERT_BATCH_SIZE", 1000
        ),
        "sync_upsert_timeout": getattr(
            settings, "BULK_DRF_SYNC_UPSERT_TIMEOUT", 30
        ),  # 30 seconds
        # Logging Settings
        # BULK_DRF_LOG_LEVEL: Set the logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        # BULK_DRF_ENABLE_DEBUG_LOGGING: Set to True to enable debug-level logging for bulk operations
        # BULK_DRF_FORCE_STDOUT: Set to True to force all logs to stdout (fixes DRF log suppression)
        # BULK_DRF_LOG_TO_FILE: Set to True to also log to files
        "log_level": getattr(settings, "BULK_DRF_LOG_LEVEL", "WARNING"),
        "enable_debug_logging": getattr(
            settings, "BULK_DRF_ENABLE_DEBUG_LOGGING", False
        ),
        "force_stdout_logging": getattr(
            settings, "BULK_DRF_FORCE_STDOUT", False
        ),
        "log_to_file": getattr(
            settings, "BULK_DRF_LOG_TO_FILE", False
        ),
        "log_file_path": getattr(
            settings, "BULK_DRF_LOG_FILE_PATH", "django_bulk_drf.log"
        ),
        # Performance Settings
        "direct_processing_threshold": getattr(
            settings, "BULK_DRF_DIRECT_PROCESSING_THRESHOLD", 5000
        ),
        "optimized_batch_size": getattr(
            settings, "BULK_DRF_OPTIMIZED_BATCH_SIZE", 2000
        ),
        "timing_log_threshold": getattr(
            settings, "BULK_DRF_TIMING_LOG_THRESHOLD", 0
        ),  # 0 = always log timing, >0 = log only for datasets larger than this
        "skip_serialization_threshold": getattr(
            settings, "BULK_DRF_SKIP_SERIALIZATION_THRESHOLD", 0
        ),  # Skip serialization for datasets larger than this (0 = never skip)
        "force_direct_processing": getattr(
            settings, "BULK_DRF_FORCE_DIRECT_PROCESSING", False
        ),  # Force direct processing instead of Celery for testing
        "force_fallback_upsert": getattr(
            settings, "BULK_DRF_FORCE_FALLBACK_UPSERT", False
        ),  # Force separate create/update instead of bulk_create with update_conflicts
    }
