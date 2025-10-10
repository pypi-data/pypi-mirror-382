"""
Django Bulk DRF - Enhanced operations for Django REST Framework

Provides a unified mixin that enhances standard ViewSet endpoints with synchronous
bulk operations for efficient database processing.
"""

__version__ = "0.1.81"
__author__ = "Konrad Beck"
__email__ = "konrad.beck@merchantcapital.co.za"

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
