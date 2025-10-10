"""
Operation mixins for DRF ViewSets.

Provides a unified mixin that enhances standard ViewSet endpoints with efficient
synchronous bulk operations using query parameters.
"""

from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django_bulk_drf.config import get_bulk_drf_settings


class BulkModelViewSet:
    """
    Enhanced ViewSet mixin providing efficient bulk operations.

    Provides optimized bulk database operations for arrays while maintaining
    standard behavior for single instances.

    Simple routing strategy:
    - Single instances (dict): Direct database operations
    - Arrays (list): Optimized bulk database operations

    Enhanced endpoints:
    - GET    /api/model/?ids=1                    # Direct single get
    - GET    /api/model/?ids=1,2,3               # Bulk multi-get
    - POST   /api/model/?unique_fields=...       # Smart upsert routing
    - PATCH  /api/model/?unique_fields=...      # Smart upsert routing
    - PUT    /api/model/?unique_fields=...      # Smart upsert routing

    Relies on DRF's built-in payload size limits for request validation.
    Optimizes database operations for maximum performance.
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
        - POST /api/model/                                    # Bulk create (array data)
        - POST /api/model/?unique_fields=field1,field2       # Bulk upsert (array data)
        """
        unique_fields_param = request.query_params.get("unique_fields")

        if isinstance(request.data, list):
            # Array data - route based on unique_fields presence
            if unique_fields_param:
                return self._sync_upsert(request, unique_fields_param)
            else:
                return self._handle_bulk_create(request)
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
        Handle PATCH requests on the base endpoint for upsert operations.

        DRF doesn't handle PATCH on base endpoints by default, so we add this method
        to support: PATCH /api/model/?unique_fields=field1,field2

        Requires:
        - unique_fields query parameter
        - Array or object data in request body
        - Performs upsert: creates new records or updates existing ones
        """
        unique_fields_param = request.query_params.get("unique_fields")
        request_data = request.data

        # Check for unique_fields parameter
        if not unique_fields_param:
            raise ValidationError("Missing required parameter: unique_fields")

        # Check for valid data type
        if not isinstance(request_data, (list, dict)):
            raise ValidationError(
                f"Invalid data type. Expected array or object, got {type(request_data).__name__}"
            )

        return self._sync_upsert(
            request, unique_fields_param, request_data=request_data
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
        raise ValidationError("PUT on list endpoint requires 'unique_fields' parameter and array data")

    # =============================================================================
    # Sync Operation Implementations
    # =============================================================================

    def _sync_multi_get(self, request, ids_param):
        """Handle multi-get for one or more items."""
        try:
            ids_list = [int(id_str.strip()) for id_str in ids_param.split(",")]
        except ValueError:
            raise ValidationError("Invalid ID format. Use comma-separated integers.")

        # Direct database query for all items
        queryset = self.get_queryset().filter(id__in=ids_list)
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "count": len(serializer.data),
                "results": serializer.data,
                "operation_type": "multi_get",
            }
        )

    def _sync_upsert(self, request, unique_fields_param, request_data=None):
        """Handle upsert operations for single items and arrays."""
        # Parse parameters
        unique_fields = [f.strip() for f in unique_fields_param.split(",") if f.strip()]

        update_fields_param = request.query_params.get("update_fields")
        update_fields = None
        if update_fields_param:
            update_fields = [
                f.strip() for f in update_fields_param.split(",") if f.strip()
            ]

        # Use pre-parsed data from caller if available
        data_payload = request_data if request_data is not None else request.data

        # Simple routing: dict for single, list for array
        if isinstance(data_payload, dict):
            # Single instance - direct database operations
            return self._handle_single_upsert(
                request, unique_fields, update_fields, data_payload
            )
        elif isinstance(data_payload, list):
            # Array - use direct bulk operations
            return self._handle_array_upsert_direct(
                request, unique_fields, update_fields, data_payload
            )
        else:
            raise ValidationError("Expected dict or array data for upsert operations.")

    def _handle_single_upsert(self, request, unique_fields, update_fields, data_dict):
        """Handle single instance upsert using direct database operations."""
        if not unique_fields:
            raise ValidationError("unique_fields parameter is required for upsert operations")

        # Auto-infer update_fields if not provided
        if not update_fields:
            update_fields = self._infer_update_fields([data_dict], unique_fields)

        # Use direct database operations for single instance
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model

        try:
            # Try to find existing instance
            unique_filter = {}
            for field in unique_fields:
                if field in data_dict:
                    unique_filter[field] = data_dict[field]

            existing_instance = None
            if unique_filter:
                existing_instance = model_class.objects.filter(**unique_filter).first()

            if existing_instance:
                # Update existing instance
                if update_fields:
                    update_data = {
                        k: v for k, v in data_dict.items() if k in update_fields
                    }
                else:
                    update_data = {
                        k: v for k, v in data_dict.items() if k not in unique_fields
                    }

                for field, value in update_data.items():
                    setattr(existing_instance, field, value)
                existing_instance.save()

                serializer = serializer_class(existing_instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Create new instance
                serializer = serializer_class(data=data_dict)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    raise ValidationError({
                        "errors": [
                            {
                                "index": 0,
                                "error": str(serializer.errors),
                                "data": data_dict,
                            }
                        ],
                    })

        except Exception as e:
            raise ValidationError(f"Direct upsert failed: {str(e)}")

    def _handle_bulk_create(self, request):
        """Handle bulk create operations using direct database operations."""
        data_list = request.data
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model

        instances_to_create = []
        errors = []

        # Validate all items
        for index, item_data in enumerate(data_list):
            try:
                serializer = serializer_class(data=item_data)
                if serializer.is_valid():
                    instances_to_create.append(model_class(**serializer.validated_data))
                else:
                    errors.append(
                        {
                            "index": index,
                            "error": serializer.errors,
                            "data": item_data,
                        }
                    )
            except Exception as e:
                errors.append(
                    {
                        "index": index,
                        "error": str(e),
                        "data": item_data,
                    }
                )

        # Return errors if any
        if errors:
            raise ValidationError({"errors": errors, "error_count": len(errors)})

        # Bulk create
        if instances_to_create:
            created_instances = model_class.objects.bulk_create(instances_to_create)
            serializer = serializer_class(created_instances, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response([], status=status.HTTP_200_OK)

    def _handle_array_upsert_direct(
        self, request, unique_fields, update_fields, data_list
    ):
        """
        Optimized bulk upsert with efficient batch processing.
        """
        import time
        import sys
        
        overall_start = time.time()
        print(f"[PERF] Starting upsert for {len(data_list)} items", file=sys.stderr)
        
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model

        # Step 1: Validate and prepare instances
        instances_to_upsert, errors = self._validate_and_prepare_instances(
            data_list, unique_fields, serializer_class, model_class
        )

        if errors:
            raise ValidationError({"errors": errors, "error_count": len(errors)})

        if not instances_to_upsert:
            return Response([], status=status.HTTP_200_OK)

        # Step 2: Infer update fields if not provided
        if not update_fields:
            update_fields = self._get_update_fields(
                data_list, unique_fields, model_class
            )

        # Step 3: Perform bulk upsert
        try:
            upserted_instances = self._perform_bulk_upsert(
                instances_to_upsert, unique_fields, update_fields, model_class
            )

            # Step 4: Build and return response
            response_start = time.time()
            response = self._build_upsert_response(
                request, upserted_instances, serializer_class
            )
            response_time = time.time() - response_start
            print(f"[PERF] Build response: {response_time:.2f}s", file=sys.stderr)
            
            total_time = time.time() - overall_start
            print(f"[PERF] Total upsert operation: {total_time:.2f}s", file=sys.stderr)
            
            return response

        except Exception as e:
            raise ValidationError(
                self._build_upsert_error_message(e, unique_fields, update_fields)
            )

    def _validate_and_prepare_instances(
        self, data_list, unique_fields, serializer_class, model_class
    ):
        """
        Validate data and prepare model instances for upsert.
        
        Validation is independent of whether records exist - the serializer
        just validates the input data. The upsert operation handles matching.
        
        Returns:
            tuple: (instances_to_upsert, errors)
        """
        import time
        import sys
        
        start_time = time.time()
        instances_to_upsert = []
        errors = []
        base_context = {"upsert_mode": True}
        
        # Create a SINGLE serializer to reuse for all validations
        # This is reused for all validations - major performance win!
        serializer_template = serializer_class(context=base_context)

        # Validate all items using shared serializer template
        validation_start = time.time()
        for index, item_data in enumerate(data_list):
            try:
                # Use the serializer's to_internal_value to handle FK conversion
                # (business -> business_id) and then validate
                # This reuses the same serializer instance for performance
                serializer_template._data = None  # Reset state
                serializer_template._errors = None
                serializer_template.initial_data = item_data
                
                # to_internal_value handles:
                # 1. FK conversion (business -> business_id) 
                # 2. Field validation via run_validation
                try:
                    validated_data = serializer_template.to_internal_value(item_data)
                except ValidationError as e:
                    errors.append(
                        {
                            "index": index,
                            "error": e.detail,
                            "data": item_data,
                        }
                    )
                    continue

                # Create instance from validated data (now has business_id, not business)
                new_instance = model_class(**validated_data)
                instances_to_upsert.append(new_instance)

            except Exception as e:
                errors.append(
                    {
                        "index": index,
                        "error": f"Processing error: {str(e)}",
                        "data": item_data,
                    }
                )

        validation_time = time.time() - validation_start
        total_time = time.time() - start_time
        print(f"[PERF] Validation loop (optimized): {validation_time:.2f}s for {len(data_list)} items ({validation_time/len(data_list)*1000:.2f}ms per item)", file=sys.stderr)
        print(f"[PERF] Total validation phase: {total_time:.2f}s", file=sys.stderr)

        return instances_to_upsert, errors

    def _get_update_fields(self, data_list, unique_fields, model_class):
        """Get update fields, auto-inferring if necessary."""
        update_fields = self._infer_update_fields(data_list, unique_fields)
        if not update_fields:
            # Get all model fields except unique_fields and auto fields
            model_fields = [f.name for f in model_class._meta.fields]
            auto_fields = ["id", "created_at", "updated_at"]
            unique_fields_set = set(unique_fields)
            update_fields = [
                field
                for field in model_fields
                if field not in unique_fields_set and field not in auto_fields
            ]
        return update_fields

    def _perform_bulk_upsert(
        self, instances_to_upsert, unique_fields, update_fields, model_class
    ):
        """
        Perform the actual bulk upsert operation.
        
        Tries optimized bulk_create with update_conflicts first,
        falls back to separate create/update if needed.
        """
        import time
        import sys
        
        start_time = time.time()
        settings = get_bulk_drf_settings()
        batch_size = settings.get("optimized_batch_size", 2000)

        # For large datasets, use smaller batches to avoid database locks
        if len(instances_to_upsert) > 5000:
            batch_size = 1000

        force_fallback = settings.get("force_fallback_upsert", False)

        # Try optimized bulk_create approach first
        if not force_fallback:
            try:
                result = model_class.objects.bulk_create(
                    instances_to_upsert,
                    update_conflicts=True,
                    update_fields=update_fields,
                    unique_fields=unique_fields,
                    batch_size=batch_size,
                )
                upsert_time = time.time() - start_time
                print(f"[PERF] Bulk upsert (optimized): {upsert_time:.2f}s for {len(instances_to_upsert)} items", file=sys.stderr)
                return result
            except Exception as e:
                # Fall through to fallback method
                print(f"[PERF] Optimized bulk_create failed: {str(e)}, falling back", file=sys.stderr)
                pass

        # Fallback: separate create and update operations
        fallback_start = time.time()
        result = self._perform_fallback_upsert(
            instances_to_upsert, unique_fields, update_fields, model_class, batch_size
        )
        fallback_time = time.time() - fallback_start
        print(f"[PERF] Bulk upsert (fallback): {fallback_time:.2f}s for {len(instances_to_upsert)} items", file=sys.stderr)
        return result

    def _perform_fallback_upsert(
        self, instances_to_upsert, unique_fields, update_fields, model_class, batch_size
    ):
        """
        Fallback upsert using separate create and update operations.
        
        This is used when bulk_create with update_conflicts is not supported
        or fails.
        """
        # Find existing records
        existing_records = self._find_existing_records(
            instances_to_upsert, unique_fields, model_class
        )

        # Separate into create/update
        instances_to_create, instances_to_update = self._separate_create_update(
            instances_to_upsert, unique_fields, update_fields, existing_records
        )

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

        # Combine and return results
        return list(created_instances) + instances_to_update

    def _find_existing_records(self, instances_to_upsert, unique_fields, model_class):
        """Find all existing records that match the unique fields."""
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

            existing_queryset = model_class.objects.filter(combined_query)
            existing_records = {
                tuple(getattr(obj, field) for field in unique_fields): obj
                for obj in existing_queryset
            }

        return existing_records

    def _separate_create_update(
        self, instances_to_upsert, unique_fields, update_fields, existing_records
    ):
        """Separate instances into those to create vs update."""
        instances_to_create = []
        instances_to_update = []

        for instance in instances_to_upsert:
            unique_key = tuple(getattr(instance, field) for field in unique_fields)
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

        return instances_to_create, instances_to_update

    def _build_upsert_response(self, request, upserted_instances, serializer_class):
        """Build the response for a successful upsert operation."""
        prefer_header = (request.headers.get("Prefer", "") or "").lower()
        prefer_minimal = "return=minimal" in prefer_header

        if not upserted_instances:
            return Response([], status=status.HTTP_200_OK)

        if prefer_minimal:
            response_data = {
                "message": f"Successfully upserted {len(upserted_instances)} instances",
                "count": len(upserted_instances),
                "serialization_skipped": True,
            }
        else:
            serializer = serializer_class(upserted_instances, many=True)
            response_data = serializer.data

        return Response(response_data, status=status.HTTP_200_OK)

    def _build_upsert_error_message(self, exception, unique_fields, update_fields):
        """Build detailed error message for upsert failures."""
        error_message = str(exception).lower()
        
        if "unique constraint" in error_message or "unique_fields" in error_message:
            detailed_error = (
                "Unique constraint error during upsert. "
                f"Ensure that fields {unique_fields} form a unique constraint in your database. "
                "If you're using a multi-column unique constraint, make sure it's properly defined."
            )
        elif "cannot force an update" in error_message or "no primary key" in error_message:
            detailed_error = (
                "Upsert operation failed due to primary key conflicts. "
                "This usually occurs when trying to update existing records without proper primary key handling."
            )
        else:
            detailed_error = f"Bulk upsert failed: {str(exception)}"

        return {
            "error": "Bulk upsert failed",
            "details": detailed_error,
            "unique_fields": unique_fields,
            "update_fields": update_fields,
        }

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
