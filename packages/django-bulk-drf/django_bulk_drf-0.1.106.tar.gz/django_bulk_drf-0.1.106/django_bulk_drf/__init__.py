"""
Django Bulk DRF - Enhanced operations for Django REST Framework

Provides a unified mixin that enhances standard ViewSet endpoints with synchronous
bulk operations that execute heavy database work (including triggers) in Celery workers
while maintaining synchronous API behavior for clients.
"""

import logging

__version__ = "0.1.81"
__author__ = "Konrad Beck"
__email__ = "konrad.beck@merchantcapital.co.za"

# Configure package logging - packages should add NullHandler by default
# This prevents logs from appearing unless explicitly configured by the user
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Make common imports available at package level
from .viewset import BulkModelViewSet
from .serializers import BulkModelSerializer
from .config import validate_bulk_drf_config, get_bulk_drf_settings

__all__ = [
    "BulkModelViewSet",  # Primary class name
    "validate_bulk_drf_config",
    "get_bulk_drf_settings",
    "BulkModelSerializer",
]
