# Django Bulk DRF

Advanced operation extensions for Django REST Framework providing intelligent sync/async routing with a clean, unified API design.

**Note:** This is a complete rewrite with modern architecture and settings. No backwards compatibility with django-drf-extensions.

## Installation

```bash
pip install django-bulk-drf
```

### Requirements

- Python 3.11+
- Django 4.0+
- Django REST Framework 3.14+

## Quick Setup

1. Add to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... your other apps
    'rest_framework',
    'django_bulk_drf',
]
```

2. (Optional) Configure cache for progress tracking:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

## Overview

This package extends Django REST Framework with a unified mixin that provides efficient bulk operations for handling large datasets.

### Key Features

1. **Enhanced Standard Endpoints**: Smart bulk operations for immediate results
2. **Intelligent Processing**: Optimized database operations for large datasets  
3. **Bulk Operations**: Efficient create, update, upsert, and delete operations
4. **Progress Tracking**: Cache-based monitoring for operations
5. **Status Management**: Comprehensive operation status and results

## Features

- ✅ **Unified API Design**: Single mixin provides comprehensive bulk capabilities
- ✅ **Smart Standard Endpoints**: Enhanced ViewSet methods with intelligent array handling
- ✅ **Efficient Bulk Operations**: Optimized database operations for large datasets
- ✅ **Immediate Results**: Direct operations with instant feedback
- ✅ **Scalable Processing**: Efficient handling of large datasets
- ✅ **Progress Tracking**: Cache-based progress monitoring
- ✅ **Comprehensive Error Handling**: Detailed validation and error reporting per item
- ✅ **Result Persistence**: Automatic caching of results for fast retrieval
- ✅ **Full Validation**: Complete DRF serializer validation ensuring data integrity
- ✅ **Transaction Safety**: Atomic database operations with rollback on failures

## Package Philosophy

This package provides a modern approach to bulk operations by offering:

1. **Clean API Design**: Enhances existing endpoints rather than creating parallel ones
2. **Efficient Processing**: Optimized database operations for maximum performance
3. **Unified Architecture**: Single mixin extends your ViewSets without complexity
4. **Production-Ready**: Built-in monitoring, error handling, and progress tracking

## Usage

### Adding Extensions to a ViewSet

```python
from rest_framework import viewsets
from django_bulk_drf.mixins import BulkOperationsMixin

class ContractViewSet(BulkOperationsMixin, viewsets.ModelViewSet):
    """
    Enhanced ViewSet with efficient bulk operations.
    
    Provides:
    - Standard CRUD operations
    - Efficient bulk operations for large datasets
    - Smart upsert capabilities
    """
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
```

Your ViewSet now provides these endpoints:

```bash
# Standard ModelViewSet endpoints (enhanced for arrays)
GET    /api/contracts/                    # List (enhanced with ?ids= support)
POST   /api/contracts/                    # Create (enhanced with array + ?unique_fields= support)
GET    /api/contracts/{id}/               # Retrieve single
PATCH  /api/contracts/                    # Update (enhanced with array + ?unique_fields= support)
PUT    /api/contracts/                    # Replace (enhanced with array + ?unique_fields= support)
DELETE /api/contracts/{id}/               # Delete single
```

## API Design

### Enhanced Standard Endpoints

Smart enhancements to standard ViewSet methods for efficient bulk operations:

#### Multi-Get
```bash
# Retrieve multiple items by IDs
GET /api/contracts/?ids=1,2,3,4,5

# Response
{
  "count": 5,
  "results": [...],
  "operation_type": "multi_get"
}
```

#### Bulk Upsert
```bash
# Bulk upsert with unique fields
POST /api/contracts/?unique_fields=contract_number,year
Content-Type: application/json
[
  {"contract_number": "C001", "year": 2024, "amount": 1000},
  {"contract_number": "C002", "year": 2024, "amount": 2000}
]

# Response (full data)
[
  {"id": 123, "contract_number": "C001", "year": 2024, "amount": 1000},
  {"id": 124, "contract_number": "C002", "year": 2024, "amount": 2000}
]

# For large datasets, skip serialization for faster response
POST /api/contracts/?unique_fields=contract_number,year
Prefer: return=minimal
Content-Type: application/json
[...10000 records...]

# Response (minimal - much faster!)
{
  "message": "Successfully upserted 10000 instances",
  "count": 10000,
  "serialization_skipped": true
}
```

## Operation Types

### Bulk Operations
- **Best for**: Any size dataset that needs efficient processing
- **Use cases**: Data imports, batch processing, CSV uploads, API integrations
- **Response**: Immediate results with full data
- **Endpoints**: Enhanced standard ViewSet methods

## Configuration

### Custom Settings

```python
# Core Settings
BULK_DRF_CHUNK_SIZE = 100                    # Items per processing chunk
BULK_DRF_MAX_RECORDS = 10000                 # Maximum records per operation
BULK_DRF_BATCH_SIZE = 1000                   # Database batch size
BULK_DRF_CACHE_TIMEOUT = 86400               # Cache timeout (24 hours)
BULK_DRF_PROGRESS_UPDATE_INTERVAL = 10       # Progress update frequency

# Sync Operation Settings
BULK_DRF_SYNC_UPSERT_MAX_ITEMS = 50          # Max items for sync upsert
BULK_DRF_SYNC_UPSERT_BATCH_SIZE = 1000       # Batch size for sync operations
BULK_DRF_SYNC_UPSERT_TIMEOUT = 30            # Timeout for sync operations (seconds)

# Advanced Settings
BULK_DRF_USE_OPTIMIZED_TASKS = True          # Enable task optimizations
BULK_DRF_AUTO_OPTIMIZE_QUERIES = True        # Auto-optimize database queries
BULK_DRF_QUERY_TIMEOUT = 300                 # Query timeout (5 minutes)
BULK_DRF_ENABLE_METRICS = False              # Enable performance metrics
```

## Example Usage

### Basic Contract Management

```python
# Bulk upsert operations
curl -X POST "/api/contracts/?unique_fields=contract_number" \
  -H "Content-Type: application/json" \
  -d '[
    {"contract_number": "C001", "amount": 1000},
    {"contract_number": "C002", "amount": 2000}
  ]'

# Bulk create operations
curl -X POST "/api/contracts/" \
  -H "Content-Type: application/json" \
  -d '[...500 contracts...]'
```

### Migration from Previous Versions

If you're coming from older versions:

```python
# Old (separate mixins)
class ContractViewSet(SyncUpsertMixin, BulkOperationsMixin, viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer

# New (unified mixin)
class ContractViewSet(BulkModelViewSet, viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
```

## Error Handling

The system provides comprehensive error handling:

- **Validation Errors**: Field-level validation using DRF serializers
- **Size Limits**: Automatic routing suggestion for oversized sync requests
- **Database Errors**: Transaction rollback on failures
- **Task Failures**: Detailed error reporting in async task status

## Performance Considerations

- **Database Efficiency**: Uses optimized database operations for all bulk processing
- **Memory Management**: Processes large datasets in configurable chunks
- **Efficient Processing**: Direct database operations for maximum performance
- **Progress Tracking**: Cache-based monitoring without database overhead
- **Result Caching**: Efficient caching of operation results

### Performance Optimization Tips

#### 1. **Use `Prefer: return=minimal` for Large Operations**

When upserting/creating large datasets (1000+ records), skip response serialization:

```python
# Python requests example
headers = {'Prefer': 'return=minimal'}
response = requests.post(
    '/api/contracts/?unique_fields=contract_number',
    json=data,
    headers=headers
)
# Response: {"message": "Successfully upserted 10000 instances", "count": 10000}
```

**Performance impact**: Can reduce response time by 80%+ for large operations (e.g., 55s → 9s for 10,000 records)

#### 2. **Optimize Serializers for Bulk Operations**

If your serializer has related fields, optimize response serialization:

```python
class ContractSerializer(BulkModelSerializer):
    class Meta:
        model = Contract
        fields = ['id', 'contract_number', 'amount']
        
    def get_queryset(self):
        # Use select_related/prefetch_related to avoid N+1 queries
        return Contract.objects.select_related('customer', 'account')
```

#### 3. **Batch Size Configuration**

Adjust batch sizes based on your data:

```python
# For smaller records (few fields)
BULK_DRF_BATCH_SIZE = 2000

# For larger records (many fields, large text)
BULK_DRF_BATCH_SIZE = 500
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
