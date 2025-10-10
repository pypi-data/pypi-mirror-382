"""
Operation mixins for DRF ViewSets.

Provides a unified mixin that enhances standard ViewSet endpoints with efficient
synchronous bulk operations using query parameters.
"""

import logging

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from django_bulk_drf.config import get_bulk_drf_settings
from django_bulk_drf.processing import (
    async_create_task,
    async_get_task,
    async_upsert_task,
)

logger = logging.getLogger(__name__)


class BulkModelViewSet:
    """
    Enhanced ViewSet mixin providing intelligent bulk operations with automatic routing.

    Automatically routes between synchronous and asynchronous processing based on data size
    and complexity while maintaining a unified API design.

    Simple routing strategy:
    - Single instances (dict): Direct database operations (no Celery overhead)
    - Arrays (list): Celery workers for heavy lifting (triggers fire in workers)

    Enhanced endpoints:
    - GET    /api/model/?ids=1                    # Direct single get
    - GET    /api/model/?ids=1,2,3               # Celery multi-get
    - POST   /api/model/?unique_fields=...       # Smart upsert routing
    - PATCH  /api/model/?unique_fields=...      # Smart upsert routing
    - PUT    /api/model/?unique_fields=...      # Smart upsert routing

    Relies on DRF's built-in payload size limits for request validation.
    Maintains synchronous API behavior while optimizing performance and resource usage.
    Database triggers fire in the appropriate execution context based on payload type.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        """Handle array data for serializers with upsert context."""
        try:
            data = kwargs.get("data", None)
            if data is not None and isinstance(data, list):
                kwargs["many"] = True

            serializer = super().get_serializer(*args, **kwargs)

            return serializer
        except Exception:
            raise

    # =============================================================================
    # Enhanced Standard ViewSet Methods (Sync Operations)
    # =============================================================================

    def list(self, request, *args, **kwargs):
        """
        Enhanced list endpoint that supports multi-get via ?ids= parameter.

        - GET /api/model/                    # Standard list
        - GET /api/model/?ids=1,2,3          # Sync multi-get (small datasets)
        """
        ids_param = request.query_params.get("ids")
        if ids_param:
            return self._sync_multi_get(request, ids_param)

        # Standard list behavior
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Enhanced create endpoint that supports bulk operations.

        - POST /api/model/                                    # Standard single create (dict data)
        - POST /api/model/                                    # Bulk create (array data, uses Celery)
        - POST /api/model/?unique_fields=field1,field2       # Bulk upsert (array data, uses Celery)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        logger.debug(
            f"BulkOperationsMixin.create() - unique_fields_param: {unique_fields_param}, data_type: {type(request.data)}, is_list: {isinstance(request.data, list)}"
        )

        if isinstance(request.data, list):
            # Array data - route based on unique_fields presence
            if unique_fields_param:
                logger.debug(
                    f"BulkOperationsMixin.create() - Routing to bulk upsert with unique_fields: {unique_fields_param}"
                )
                return self._sync_upsert(request, unique_fields_param)
            else:
                logger.debug(
                    "BulkOperationsMixin.create() - Routing to bulk create (no unique_fields)"
                )
                return self._handle_bulk_create(request)

        logger.debug(
            "BulkOperationsMixin.create() - Using standard single create behavior"
        )
        # Standard single create behavior
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Enhanced update endpoint that supports sync upsert via query params.

        - PUT /api/model/{id}/                               # Standard single update
        - PUT /api/model/?unique_fields=field1,field2       # Sync upsert (array data)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if unique_fields_param and isinstance(request.data, list):
            return self._sync_upsert(request, unique_fields_param)

        # Standard single update behavior
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Enhanced partial update endpoint that supports sync upsert via query params.

        - PATCH /api/model/{id}/                             # Standard single partial update
        - PATCH /api/model/?unique_fields=field1,field2     # Sync upsert (array data)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if unique_fields_param and isinstance(request.data, list):
            return self._sync_upsert(request, unique_fields_param)

        # Standard single partial update behavior
        return super().partial_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests on list endpoint for sync upsert.

        DRF doesn't handle PATCH on list endpoints by default, so we add this method
        to support: PATCH /api/model/?unique_fields=field1,field2
        """
        unique_fields_param = request.query_params.get("unique_fields")
        preparsed_list = request.data

        if unique_fields_param and isinstance(preparsed_list, list):
            return self._sync_upsert(
                request, unique_fields_param, preparsed_data=preparsed_list
            )

        # If no unique_fields or not array data, this is invalid
        return Response(
            {
                "error": "PATCH on list endpoint requires 'unique_fields' parameter and array data"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests on list endpoint for sync upsert.

        DRF doesn't handle PUT on list endpoints by default, so we add this method
        to support: PUT /api/model/?unique_fields=field1,field2
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if unique_fields_param and isinstance(request.data, list):
            return self._sync_upsert(request, unique_fields_param)

        # If no unique_fields or not array data, this is invalid
        return Response(
            {
                "error": "PUT on list endpoint requires 'unique_fields' parameter and array data"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # =============================================================================
    # Sync Operation Implementations
    # =============================================================================

    def _sync_multi_get(self, request, ids_param):
        """Handle sync multi-get - direct for single items, Celery for arrays."""
        try:
            ids_list = [int(id_str.strip()) for id_str in ids_param.split(",")]
        except ValueError:
            return Response(
                {"error": "Invalid ID format. Use comma-separated integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Simple routing: single item direct, arrays via Celery
        if len(ids_list) == 1:
            # Single item - direct database call
            return self._handle_single_get(ids_list[0])
        else:
            # Multiple items - use Celery workers
            return self._handle_array_get(request, ids_list)

    def _handle_single_get(self, item_id):
        """Handle single item retrieval directly without Celery overhead."""
        try:
            queryset = self.get_queryset().filter(id=item_id)
            instance = queryset.first()

            if instance:
                serializer = self.get_serializer(instance)
                return Response(
                    {
                        "count": 1,
                        "results": [serializer.data],
                        "is_sync": True,
                        "operation_type": "direct_get",
                    }
                )
            else:
                return Response(
                    {"error": f"Item with id {item_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {"error": f"Direct get failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_array_get(self, request, ids_list):
        """Handle array retrieval using Celery workers."""
        # Use Celery worker for multiple items
        model_class = self.get_queryset().model
        model_class_path = f"{model_class.__module__}.{model_class.__name__}"
        serializer_class = self.get_serializer_class()
        serializer_class_path = (
            f"{serializer_class.__module__}.{serializer_class.__name__}"
        )

        query_data = {"ids": ids_list}
        user_id = request.user.id if request.user.is_authenticated else None

        # Start Celery task with optimized settings
        task = async_get_task.delay(
            model_class_path, serializer_class_path, query_data, user_id
        )

        # Wait for task completion with fixed timeout
        try:
            # Wait for the task to complete (synchronous behavior)
            task_result = task.get(timeout=180)  # 3 minute timeout for get operations

            if task_result.get("success", False):
                return Response(
                    {
                        "count": task_result.get("count", 0),
                        "results": task_result.get("results", []),
                        "is_sync": True,
                        "task_id": task.id,
                        "operation_type": "sync_get_via_worker",
                    }
                )
            else:
                return Response(
                    {"error": f"Worker task failed: {task_result.get('error')}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            return Response(
                {"error": f"Task execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _sync_upsert(self, request, unique_fields_param, preparsed_data=None):
        """Handle sync upsert operations - direct for single items, Celery for arrays."""
        logger.debug(
            f"BulkOperationsMixin._sync_upsert() - Called with unique_fields_param: {unique_fields_param}"
        )

        # Parse parameters
        unique_fields = [f.strip() for f in unique_fields_param.split(",") if f.strip()]
        logger.debug(
            f"BulkOperationsMixin._sync_upsert() - Parsed unique_fields: {unique_fields}"
        )

        update_fields_param = request.query_params.get("update_fields")
        update_fields = None
        if update_fields_param:
            update_fields = [
                f.strip() for f in update_fields_param.split(",") if f.strip()
            ]
        logger.debug(
            f"BulkOperationsMixin._sync_upsert() - Parsed update_fields: {update_fields}"
        )

        # Use pre-parsed data from caller if available
        data_payload = preparsed_data if preparsed_data is not None else request.data
        logger.debug(
            f"BulkOperationsMixin._sync_upsert() - Data payload type: {type(data_payload)}, is_list: {isinstance(data_payload, list)}"
        )

        if isinstance(data_payload, list):
            logger.debug(
                f"BulkOperationsMixin._sync_upsert() - Array with {len(data_payload)} items"
            )

        # Simple routing: dict direct, list via Celery
        if isinstance(data_payload, dict):
            logger.debug(
                "BulkOperationsMixin._sync_upsert() - Routing to single upsert"
            )
            # Single instance - direct database operations
            return self._handle_single_upsert(
                request, unique_fields, update_fields, data_payload
            )
        elif isinstance(data_payload, list):
            logger.debug(
                "BulkOperationsMixin._sync_upsert() - Routing to array upsert (Celery)"
            )
            # Array - use Celery workers for heavy operations
            return self._handle_array_upsert(
                request, unique_fields, update_fields, data_payload
            )
        else:
            logger.debug(
                f"BulkOperationsMixin._sync_upsert() - Invalid data type: {type(data_payload)}"
            )
            return Response(
                {"error": "Expected dict or array data for upsert operations."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _handle_single_upsert(self, request, unique_fields, update_fields, data_dict):
        """Handle single instance upsert directly without Celery overhead."""
        logger.debug(
            f"BulkOperationsMixin._handle_single_upsert() - Processing single item: {data_dict}"
        )

        if not unique_fields:
            logger.error(
                "BulkOperationsMixin._handle_single_upsert() - ERROR: No unique_fields provided"
            )
            return Response(
                {"error": "unique_fields parameter is required for upsert operations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Auto-infer update_fields if not provided
        if not update_fields:
            update_fields = self._infer_update_fields([data_dict], unique_fields)
            logger.debug(
                f"BulkOperationsMixin._handle_single_upsert() - Auto-inferred update_fields: {update_fields}"
            )

        # Use direct database operations for single instance
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model
        logger.debug(
            f"BulkOperationsMixin._handle_single_upsert() - Using model: {model_class.__name__}"
        )

        try:
            # Try to find existing instance
            unique_filter = {}
            for field in unique_fields:
                if field in data_dict:
                    unique_filter[field] = data_dict[field]

            logger.debug(
                f"BulkOperationsMixin._handle_single_upsert() - Unique filter: {unique_filter}"
            )

            existing_instance = None
            if unique_filter:
                existing_instance = model_class.objects.filter(**unique_filter).first()
                logger.debug(
                    f"BulkOperationsMixin._handle_single_upsert() - Existing instance found: {existing_instance is not None}"
                )

            if existing_instance:
                logger.debug(
                    f"BulkOperationsMixin._handle_single_upsert() - Updating existing instance ID: {existing_instance.id}"
                )
                # Update existing instance
                if update_fields:
                    update_data = {
                        k: v for k, v in data_dict.items() if k in update_fields
                    }
                else:
                    update_data = {
                        k: v for k, v in data_dict.items() if k not in unique_fields
                    }

                logger.debug(
                    f"BulkOperationsMixin._handle_single_upsert() - Update data: {update_data}"
                )

                for field, value in update_data.items():
                    setattr(existing_instance, field, value)
                existing_instance.save()

                serializer = serializer_class(existing_instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.debug(
                    "BulkOperationsMixin._handle_single_upsert() - Creating new instance"
                )
                # Create new instance
                serializer = serializer_class(data=data_dict)
                if serializer.is_valid():
                    instance = serializer.save()
                    logger.debug(
                        f"BulkOperationsMixin._handle_single_upsert() - Created instance ID: {instance.id}"
                    )
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    logger.error(
                        f"BulkOperationsMixin._handle_single_upsert() - Validation failed: {serializer.errors}"
                    )
                    return Response(
                        {
                            "error": "Validation failed",
                            "errors": [
                                {
                                    "index": 0,
                                    "error": str(serializer.errors),
                                    "data": data_dict,
                                }
                            ],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Exception as e:
            logger.error(
                f"BulkOperationsMixin._handle_single_upsert() - ERROR: {str(e)}"
            )
            return Response(
                {"error": f"Direct upsert failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_bulk_create(self, request):
        """Handle bulk create operations using Celery workers."""
        data_list = request.data
        logger.debug(
            f"BulkOperationsMixin._handle_bulk_create() - Processing bulk create with {len(data_list)} items"
        )

        # Use Celery worker for bulk create
        serializer_class = self.get_serializer_class()
        serializer_class_path = (
            f"{serializer_class.__module__}.{serializer_class.__name__}"
        )
        user_id = request.user.id if request.user.is_authenticated else None

        # Start Celery bulk create task
        logger.debug(
            "BulkOperationsMixin._handle_bulk_create() - Dispatching bulk create to Celery"
        )
        task = async_create_task.delay(serializer_class_path, data_list, user_id)
        logger.debug(
            f"BulkOperationsMixin._handle_bulk_create() - Task dispatched with ID: {task.id}"
        )

        # Wait for task completion
        try:
            logger.debug(
                "BulkOperationsMixin._handle_bulk_create() - Waiting for task completion (300s timeout)..."
            )
            # Wait for the task to complete (synchronous behavior)
            task_result = task.get(
                timeout=300
            )  # 5 minute timeout for bulk create operations
            logger.debug(
                "BulkOperationsMixin._handle_bulk_create() - Task completed successfully"
            )
            logger.debug(
                f"BulkOperationsMixin._handle_bulk_create() - Result: success_count={task_result.get('success_count', 0)}, error_count={task_result.get('error_count', 0)}"
            )

            # Check for errors first
            errors = task_result.get("errors", [])
            if errors:
                logger.error(
                    f"BulkOperationsMixin._handle_bulk_create() - Returning errors: {errors}"
                )
                return Response(
                    {
                        "errors": errors,
                        "error_count": task_result.get("error_count", 0),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Return successful result in standard DRF format
            serializer_class = self.get_serializer_class()
            model_class = serializer_class.Meta.model

            # Get the created instances
            created_ids = task_result.get("created_ids", [])
            if created_ids:
                created_instances = list(model_class.objects.filter(id__in=created_ids))
                serializer = serializer_class(created_instances, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # No instances were created successfully
                logger.debug(
                    "BulkOperationsMixin._handle_bulk_create() - No instances created and no errors"
                )
                return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(
                f"BulkOperationsMixin._handle_bulk_create() - ERROR: Task execution failed: {str(e)}"
            )
            return Response(
                {"error": f"Bulk create task execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_array_upsert(self, request, unique_fields, update_fields, data_list):
        """Handle array upsert using Celery workers."""
        import time

        start_time = time.time()

        logger.debug("=== ARRAY UPSERT STARTED ===")
        logger.debug(f"Processing array with {len(data_list)} items")
        logger.debug(f"Unique fields: {unique_fields}")
        logger.debug(f"Update fields: {update_fields}")
        logger.debug("============================")

        # Smart routing: Use direct processing for smaller datasets, Celery for larger ones
        # Direct processing is faster for smaller datasets due to no Celery overhead
        # Celery is better for larger datasets to avoid blocking the web server
        settings = get_bulk_drf_settings()
        direct_threshold = settings.get("direct_processing_threshold", 5000)
        force_direct = settings.get("force_direct_processing", False)

        # TEMPORARY: Force direct processing for performance testing
        # Remove this line after testing
        force_direct = True
        logger.debug(
            "🚀 BYPASSING CELERY - Using direct processing for detailed timing analysis"
        )

        if force_direct or len(data_list) < direct_threshold:
            processing_type = "forced direct" if force_direct else "small dataset"
            logger.debug(
                f"Using direct processing ({processing_type}): {len(data_list)} items"
            )
            return self._handle_array_upsert_direct(
                request, unique_fields, update_fields, data_list
            )

        if not unique_fields:
            logger.error(
                "BulkOperationsMixin._handle_array_upsert() - ERROR: No unique_fields provided"
            )
            return Response(
                {"error": "unique_fields parameter is required for upsert operations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Auto-infer update_fields if not provided
        if not update_fields:
            update_fields = self._infer_update_fields(data_list, unique_fields)
            logger.debug(
                f"BulkOperationsMixin._handle_array_upsert() - Auto-inferred update_fields: {update_fields}"
            )

        # Use Celery worker for array operations
        serializer_class = self.get_serializer_class()
        serializer_class_path = (
            f"{serializer_class.__module__}.{serializer_class.__name__}"
        )
        logger.debug(
            f"BulkOperationsMixin._handle_array_upsert() - Using serializer: {serializer_class_path}"
        )

        user_id = request.user.id if request.user.is_authenticated else None
        logger.debug(f"BulkOperationsMixin._handle_array_upsert() - User ID: {user_id}")

        # Start Celery upsert task with optimized settings
        celery_dispatch_start = time.time()
        logger.debug("Dispatching Celery task...")

        # Pass upsert context to skip uniqueness validation
        upsert_context = {
            "skip_uniqueness_validation": True,
            "unique_fields": unique_fields,
        }

        task = async_upsert_task.delay(
            serializer_class_path,
            data_list,
            unique_fields,
            update_fields,
            user_id,
            upsert_context,
        )
        celery_dispatch_time = time.time() - celery_dispatch_start
        logger.debug(
            f"Task dispatched with ID: {task.id} (dispatch took {celery_dispatch_time:.4f}s)"
        )

        # Wait for task completion with fixed timeout
        try:
            celery_wait_start = time.time()
            logger.debug("Waiting for task completion (300s timeout)...")
            # Wait for the task to complete (synchronous behavior)
            task_result = task.get(
                timeout=300
            )  # 5 minute timeout for upsert operations
            celery_wait_time = time.time() - celery_wait_start
            logger.debug(
                f"Task completed successfully (wait took {celery_wait_time:.4f}s)"
            )
            logger.debug(
                f"Result: success_count={task_result.get('success_count', 0)}, error_count={task_result.get('error_count', 0)}"
            )

            # Check for errors first
            errors = task_result.get("errors", [])
            if errors:
                logger.error(
                    f"BulkOperationsMixin._handle_array_upsert() - Returning errors: {errors}"
                )
                return Response(
                    {
                        "errors": errors,
                        "error_count": task_result.get("error_count", 0),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Return successful result, honoring Prefer: return=minimal
            response_start = time.time()
            serializer_class = self.get_serializer_class()
            model_class = serializer_class.Meta.model

            # Get all affected instances (created and updated)
            created_ids = task_result.get("created_ids", [])
            updated_ids = task_result.get("updated_ids", [])
            all_ids = created_ids + updated_ids

            # Check Prefer header for minimal return
            prefer_header = (request.headers.get("Prefer", "") or "").lower()
            prefer_minimal = "return=minimal" in prefer_header

            if all_ids:
                if prefer_minimal:
                    # Avoid extra queries; return minimal response
                    total_time = time.time() - start_time
                    logger.debug("=== ARRAY UPSERT COMPLETED (MINIMAL) ===")
                    logger.debug(f"TOTAL TIME: {total_time:.4f}s")
                    logger.debug("TIMING BREAKDOWN:")
                    logger.debug(
                        f"  - Celery dispatch: {celery_dispatch_time:.4f}s ({celery_dispatch_time / total_time * 100:.1f}%)"
                    )
                    logger.debug(
                        f"  - Celery execution: {celery_wait_time:.4f}s ({celery_wait_time / total_time * 100:.1f}%)"
                    )
                    logger.debug(f"  - Response preparation: minimal")
                    logger.debug(f"  - TOTAL: {total_time:.4f}s")
                    logger.debug(
                        f"Processing rate: {len(data_list) / total_time:.2f} items/second"
                    )
                    logger.debug("=============================")

                    return Response(
                        {
                            "message": f"Successfully upserted {len(all_ids)} instances",
                            "count": len(all_ids),
                            "serialization_skipped": True,
                        },
                        status=status.HTTP_200_OK,
                    )

                affected_instances = list(model_class.objects.filter(id__in=all_ids))
                serializer = serializer_class(affected_instances, many=True)
                response_time = time.time() - response_start
                total_time = time.time() - start_time

                logger.debug("=== ARRAY UPSERT COMPLETED ===")
                logger.debug(f"TOTAL TIME: {total_time:.4f}s")
                logger.debug("TIMING BREAKDOWN:")
                logger.debug(
                    f"  - Celery dispatch: {celery_dispatch_time:.4f}s ({celery_dispatch_time / total_time * 100:.1f}%)"
                )
                logger.debug(
                    f"  - Celery execution: {celery_wait_time:.4f}s ({celery_wait_time / total_time * 100:.1f}%)"
                )
                logger.debug(
                    f"  - Response preparation: {response_time:.4f}s ({response_time / total_time * 100:.1f}%)"
                )
                logger.debug(f"  - TOTAL: {total_time:.4f}s")
                logger.debug(
                    f"Processing rate: {len(data_list) / total_time:.2f} items/second"
                )
                logger.debug("=============================")

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # No instances were affected and no errors
                response_time = time.time() - response_start
                total_time = time.time() - start_time

                logger.debug("=== ARRAY UPSERT COMPLETED ===")
                logger.debug(f"TOTAL TIME: {total_time:.4f}s")
                logger.debug("TIMING BREAKDOWN:")
                logger.debug(
                    f"  - Celery dispatch: {celery_dispatch_time:.4f}s ({celery_dispatch_time / total_time * 100:.1f}%)"
                )
                logger.debug(
                    f"  - Celery execution: {celery_wait_time:.4f}s ({celery_wait_time / total_time * 100:.1f}%)"
                )
                logger.debug(
                    f"  - Response preparation: {response_time:.4f}s ({response_time / total_time * 100:.1f}%)"
                )
                logger.debug(f"  - TOTAL: {total_time:.4f}s")
                logger.debug("=============================")

                return Response([], status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"BulkOperationsMixin._handle_array_upsert() - ERROR: Task execution failed: {str(e)}"
            )
            return Response(
                {"error": f"Upsert task execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_array_upsert_direct(
        self, request, unique_fields, update_fields, data_list
    ):
        """
        Optimized bulk upsert with minimal logging and efficient batch processing.
        """
        import time

        # Start timing for the entire operation
        operation_start = time.time()

        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model

        # Get settings for timing configuration
        settings = get_bulk_drf_settings()
        timing_threshold = settings.get("timing_log_threshold", 0)

        # Log start of processing based on threshold
        if len(data_list) >= timing_threshold:
            logger.debug(
                f"Direct processing: Starting bulk upsert for {len(data_list)} items"
            )
            logger.debug(f"Unique fields: {unique_fields}")
            logger.debug(f"Update fields: {update_fields}")

        instances_to_upsert = []
        errors = []

        # Optimized field conversion - process in batches
        data_processing_start = time.time()

        # Prepare serializer context for per-item validation
        base_context = {"upsert_mode": True}
        # Access field map once for conversions of unique field inputs
        serializer_field_map = serializer_class(context=base_context).fields

        # Process items in batches to avoid memory issues
        batch_size = 1000
        for batch_start in range(0, len(data_list), batch_size):
            batch_end = min(batch_start + batch_size, len(data_list))
            batch_data = data_list[batch_start:batch_end]

            for index, item_data in enumerate(batch_data):
                try:
                    # Build lookup for existing instance using unique_fields
                    lookup_filter = {}
                    for unique_field in unique_fields or []:
                        if unique_field in item_data:
                            raw_value = item_data[unique_field]
                            # Convert using serializer field if available
                            if unique_field in serializer_field_map:
                                try:
                                    converted = serializer_field_map[
                                        unique_field
                                    ].to_internal_value(raw_value)
                                except Exception:
                                    converted = raw_value
                            else:
                                converted = raw_value
                            lookup_filter[unique_field] = converted

                    existing_instance = None
                    if lookup_filter:
                        existing_instance = model_class.objects.filter(
                            **lookup_filter
                        ).first()

                    # Validate using the project's serializer; set instance to bypass unique validators
                    serializer = serializer_class(
                        instance=existing_instance,
                        data=item_data,
                        context=base_context,
                        partial=True,
                    )
                    if not serializer.is_valid():
                        logger.error(f"BulkViewSet - Serializer validation failed: {serializer.errors}")
                        logger.error(f"BulkViewSet - Data that failed: {item_data}")
                        errors.append(
                            {
                                "index": batch_start + index,
                                "error": serializer.errors,
                                "data": item_data,
                            }
                        )
                        continue

                    validated_data = serializer.validated_data
                    logger.debug(f"BulkViewSet - validated_data before model creation: {validated_data}")
                    # Create instance directly from validated data
                    new_instance = model_class(**validated_data)
                    logger.debug(f"BulkViewSet - Created model instance: business_id={getattr(new_instance, 'business_id', 'NOT_SET')}")
                    instances_to_upsert.append(new_instance)

                except Exception as e:
                    # Only log errors, not every item
                    if len(errors) < 10:  # Limit error logging
                        logger.error(
                            f"Error processing item {batch_start + index}: {e}"
                        )
                    errors.append(
                        {
                            "index": batch_start + index,
                            "error": f"Processing error: {str(e)}",
                            "data": item_data,
                        }
                    )

        data_processing_time = time.time() - data_processing_start
        if len(data_list) >= timing_threshold:
            logger.debug(
                f"Data processing completed: {data_processing_time:.4f}s for {len(data_list)} items"
            )

        # Return errors if any
        if errors:
            logger.error(
                f"BulkOperationsMixin._handle_array_upsert_direct() - Returning {len(errors)} errors"
            )
            return Response(
                {"errors": errors, "error_count": len(errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Optimized bulk upsert with minimal logging
        if instances_to_upsert:
            try:
                bulk_operation_start = time.time()

                if len(instances_to_upsert) >= timing_threshold:
                    logger.debug(
                        f"Performing bulk upsert with {len(instances_to_upsert)} instances"
                    )

                # Auto-infer update_fields if not provided (optimized)
                if not update_fields:
                    update_fields = self._infer_update_fields(data_list, unique_fields)
                    if not update_fields:
                        # Get all model fields except unique_fields and auto fields
                        model_fields = [f.name for f in model_class._meta.fields]
                        auto_fields = ["id", "created_at", "updated_at"]
                        unique_fields_set = set(unique_fields)
                        update_fields = [
                            field
                            for field in model_fields
                            if field not in unique_fields_set
                            and field not in auto_fields
                        ]

                # Optimized existing records check - use bulk_create with update_conflicts
                # This is much faster than checking each record individually
                try:
                    # Log database operation details
                    if len(instances_to_upsert) >= timing_threshold:
                        logger.debug(f"Database operation details:")
                        logger.debug(
                            f"  - Instances to upsert: {len(instances_to_upsert)}"
                        )
                        logger.debug(f"  - Update fields: {update_fields}")
                        logger.debug(f"  - Unique fields: {unique_fields}")
                        logger.debug(
                            f"  - Batch size: {settings.get('optimized_batch_size', 2000)}"
                        )

                    db_start = time.time()
                    # Use Django's bulk_create with update_conflicts for true upsert
                    # Try different batch sizes to optimize performance
                    batch_size = settings.get("optimized_batch_size", 2000)

                    # For large datasets, try smaller batches to avoid database locks
                    if len(instances_to_upsert) > 5000:
                        batch_size = 1000
                        logger.debug(
                            f"Large dataset detected, using smaller batch size: {batch_size}"
                        )

                    # Check if we should force fallback method
                    force_fallback = settings.get("force_fallback_upsert", False)

                    if force_fallback:
                        logger.debug(
                            "🚀 FORCING FALLBACK METHOD - Using separate create/update operations"
                        )
                        # Skip the try block and go directly to fallback
                        bulk_error = Exception("Forced fallback method")
                    else:
                        bulk_error = None

                    # Try the optimized bulk_create approach first
                    if not force_fallback:
                        try:
                            created_instances = model_class.objects.bulk_create(
                                instances_to_upsert,
                                update_conflicts=True,
                                update_fields=update_fields,
                                unique_fields=unique_fields,
                                batch_size=batch_size,
                            )
                            logger.debug(
                                f"Used bulk_create with update_conflicts (batch_size={batch_size})"
                            )
                        except Exception as e:
                            # Assign to the outer bulk_error variable
                            bulk_error = e

                    if force_fallback or bulk_error:
                        error_msg = str(bulk_error) if bulk_error else "forced fallback"
                        logger.warning(
                            f"bulk_create with update_conflicts failed: {error_msg}"
                        )
                        logger.debug(
                            "Falling back to separate create/update operations..."
                        )

                        # Fallback: separate create and update operations
                        # This might be faster for some database configurations
                        fallback_start = time.time()

                        # Extract unique values for existing record lookup
                        unique_values_list = []
                        for instance in instances_to_upsert:
                            unique_values = {
                                field: getattr(instance, field)
                                for field in unique_fields
                                if hasattr(instance, field)
                            }
                            if unique_values:
                                unique_values_list.append(unique_values)

                        # Single query to find existing records
                        existing_records = {}
                        if unique_values_list:
                            combined_query = Q()
                            for unique_values in unique_values_list:
                                combined_query |= Q(**unique_values)

                            existing_queryset = model_class.objects.filter(
                                combined_query
                            )
                            existing_records = {
                                tuple(
                                    getattr(obj, field) for field in unique_fields
                                ): obj
                                for obj in existing_queryset
                            }

                        # Separate into create/update
                        instances_to_create = []
                        instances_to_update = []

                        for instance in instances_to_upsert:
                            unique_key = tuple(
                                getattr(instance, field) for field in unique_fields
                            )
                            if unique_key in existing_records:
                                existing_instance = existing_records[unique_key]
                                # Update existing instance
                                for field in update_fields:
                                    if hasattr(instance, field):
                                        setattr(
                                            existing_instance,
                                            field,
                                            getattr(instance, field),
                                        )
                                instances_to_update.append(existing_instance)
                            else:
                                instances_to_create.append(instance)

                        # Perform bulk operations
                        created_instances = []
                        if instances_to_create:
                            created_instances = model_class.objects.bulk_create(
                                instances_to_create, batch_size=batch_size
                            )

                        if instances_to_update:
                            model_class.objects.bulk_update(
                                instances_to_update,
                                update_fields,
                                batch_size=batch_size,
                            )

                        # Combine results
                        all_instances = list(created_instances) + instances_to_update
                        created_instances = all_instances

                        fallback_time = time.time() - fallback_start
                        logger.debug(
                            f"Fallback operations completed in {fallback_time:.4f}s"
                        )
                        logger.debug(
                            f"Created: {len(instances_to_create)}, Updated: {len(instances_to_update)}"
                        )
                    db_time = time.time() - db_start

                    if len(instances_to_upsert) >= timing_threshold:
                        logger.debug(f"Database bulk_create completed in {db_time:.4f}s")

                    bulk_create_time = time.time() - bulk_operation_start
                    if len(instances_to_upsert) >= timing_threshold:
                        logger.debug(f"Bulk upsert completed in {bulk_create_time:.4f}s")

                    # Serialize response honoring Prefer: return=minimal
                    serialize_start = time.time()
                    prefer_header = (request.headers.get("Prefer", "") or "").lower()
                    prefer_minimal = "return=minimal" in prefer_header

                    if created_instances:
                        if prefer_minimal:
                            response_data = {
                                "message": f"Successfully upserted {len(created_instances)} instances",
                                "count": len(created_instances),
                                "serialization_skipped": True,
                            }
                        else:
                            if len(instances_to_upsert) >= timing_threshold:
                                logger.debug(
                                    f"Serializing {len(created_instances)} instances..."
                                )
                            serializer = serializer_class(created_instances, many=True)
                            response_data = serializer.data
                    else:
                        response_data = []
                    serialize_time = time.time() - serialize_start

                    if len(instances_to_upsert) >= timing_threshold:
                        logger.debug(f"Serialization completed in {serialize_time:.4f}s")

                    # Log comprehensive timing summary
                    if len(data_list) >= timing_threshold:
                        total_operation_time = time.time() - operation_start
                        logger.debug("=== DIRECT PROCESSING TIMING SUMMARY ===")
                        logger.debug(
                            f"Total operation time: {total_operation_time:.4f}s"
                        )
                        logger.debug(
                            f"Data processing time: {data_processing_time:.4f}s"
                        )
                        logger.debug(f"Database operation time: {db_time:.4f}s")
                        logger.debug(f"Serialization time: {serialize_time:.4f}s")
                        logger.debug(f"Bulk upsert time: {bulk_create_time:.4f}s")
                        logger.debug(f"Items processed: {len(data_list)}")
                        logger.debug(
                            f"Instances upserted: {len(created_instances) if created_instances else 0}"
                        )
                        logger.debug("=========================================")

                    return Response(response_data, status=status.HTTP_200_OK)

                except Exception as bulk_error:
                    # Fallback to separate create/update if bulk_create with update_conflicts fails
                    logger.warning(
                        f"Bulk create with update_conflicts failed: {bulk_error}, falling back to separate operations"
                    )

                    # Extract unique values efficiently
                    unique_values_list = []
                    for instance in instances_to_upsert:
                        unique_values = {
                            field: getattr(instance, field)
                            for field in unique_fields
                            if hasattr(instance, field)
                        }
                        if unique_values:
                            unique_values_list.append(unique_values)

                    # Single query to find existing records
                    existing_records = {}
                    if unique_values_list:
                        combined_query = Q()
                        for unique_values in unique_values_list:
                            combined_query |= Q(**unique_values)

                        existing_queryset = model_class.objects.filter(combined_query)
                        existing_records = {
                            tuple(getattr(obj, field) for field in unique_fields): obj
                            for obj in existing_queryset
                        }

                    # Separate into create/update
                    instances_to_create = []
                    instances_to_update = []

                    for instance in instances_to_upsert:
                        unique_key = tuple(
                            getattr(instance, field) for field in unique_fields
                        )
                        if unique_key in existing_records:
                            existing_instance = existing_records[unique_key]
                            # Update existing instance
                            for field in update_fields:
                                if hasattr(instance, field):
                                    setattr(
                                        existing_instance,
                                        field,
                                        getattr(instance, field),
                                    )
                            instances_to_update.append(existing_instance)
                        else:
                            instances_to_create.append(instance)

                    # Perform bulk operations
                    created_instances = []
                    if instances_to_create:
                        created_instances = model_class.objects.bulk_create(
                            instances_to_create,
                            batch_size=settings.get("optimized_batch_size", 2000),
                        )

                    if instances_to_update:
                        model_class.objects.bulk_update(
                            instances_to_update,
                            update_fields,
                            batch_size=settings.get("optimized_batch_size", 2000),
                        )

                    # Return combined results
                    all_instances = list(created_instances) + instances_to_update
                    if all_instances:
                        serializer = serializer_class(all_instances, many=True)
                        response_data = serializer.data
                    else:
                        response_data = []

                    total_time = time.time() - bulk_operation_start
                    if len(instances_to_upsert) >= timing_threshold:
                        logger.debug(f"Fallback upsert completed in {total_time:.4f}s")

                    # Log comprehensive timing summary for fallback
                    if len(data_list) >= timing_threshold:
                        total_operation_time = time.time() - operation_start
                        logger.debug(
                            "=== DIRECT PROCESSING TIMING SUMMARY (FALLBACK) ==="
                        )
                        logger.debug(
                            f"Total operation time: {total_operation_time:.4f}s"
                        )
                        logger.debug(
                            f"Data processing time: {data_processing_time:.4f}s"
                        )
                        logger.debug(f"Fallback upsert time: {total_time:.4f}s")
                        logger.debug(f"Items processed: {len(data_list)}")
                        logger.debug(f"Instances created: {len(instances_to_create)}")
                        logger.debug(f"Instances updated: {len(instances_to_update)}")
                        logger.debug("=================================================")

                    return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(
                    f"BulkOperationsMixin._handle_array_upsert_direct() - Bulk upsert failed: {e}"
                )

                # Provide more specific error messages for common issues
                error_message = str(e).lower()
                if (
                    "unique constraint" in error_message
                    or "unique_fields" in error_message
                ):
                    detailed_error = (
                        "Unique constraint error during upsert. "
                        f"Ensure that fields {unique_fields} form a unique constraint in your database. "
                        "If you're using a multi-column unique constraint, make sure it's properly defined."
                    )
                elif (
                    "cannot force an update" in error_message
                    or "no primary key" in error_message
                ):
                    detailed_error = (
                        "Upsert operation failed due to primary key conflicts. "
                        "This usually occurs when trying to update existing records without proper primary key handling."
                    )
                else:
                    detailed_error = f"Bulk upsert failed: {str(e)}"

                return Response(
                    {
                        "error": "Bulk upsert failed",
                        "details": detailed_error,
                        "unique_fields": unique_fields,
                        "update_fields": update_fields,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            logger.debug(
                "BulkOperationsMixin._handle_array_upsert_direct() - No instances to upsert"
            )
            return Response([], status=status.HTTP_200_OK)

    def _infer_update_fields(self, data_list, unique_fields):
        """Auto-infer update fields from data payload."""
        if not data_list:
            return []

        all_fields = set()
        for item in data_list:
            if isinstance(item, dict):
                all_fields.update(item.keys())

        unique_fields_set = set(unique_fields)
        return list(all_fields - unique_fields_set)
