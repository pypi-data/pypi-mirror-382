"""
Common async processing utilities for handling array operations with Celery.
"""

import logging
import traceback
from typing import Any

from celery import shared_task
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.module_loading import import_string

from django_bulk_drf.cache import OperationCache
from django_bulk_drf.logging_utils import (
    log_celery_task_start,
    log_celery_task_complete,
    log_bulk_operation_start,
    log_bulk_operation_complete,
)

logger = logging.getLogger('django_bulk_drf.processing')


class OperationResult:
    """Result container for async operations."""

    def __init__(self, task_id: str, total_items: int, operation_type: str):
        self.task_id = task_id
        self.total_items = total_items
        self.operation_type = operation_type
        self.success_count = 0
        self.error_count = 0
        self.errors: list[dict[str, Any]] = []
        self.created_ids: list[int] = []
        self.updated_ids: list[int] = []
        self.deleted_ids: list[int] = []

    def add_success(self, item_id: int | None = None, operation: str = "created"):
        self.success_count += 1
        if item_id:
            if operation == "created":
                self.created_ids.append(item_id)
            elif operation == "updated":
                self.updated_ids.append(item_id)
            elif operation == "deleted":
                self.deleted_ids.append(item_id)

    def add_error(self, index: int, error_message: str, item_data: Any = None):
        self.error_count += 1
        self.errors.append(
            {
                "index": index,
                "error": error_message,
                "data": item_data,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        result = {
            "task_id": self.task_id,
            "operation_type": self.operation_type,
            "total_items": self.total_items,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "errors": self.errors,
            "created_ids": self.created_ids,
            "updated_ids": self.updated_ids,
            "deleted_ids": self.deleted_ids,
        }
        
        # Add timing information if available
        if hasattr(self, 'timing_info'):
            result['timing_info'] = self.timing_info
            
        return result


def _build_field_filters(
    model_class, unique_fields, validated_data, result, index, item_data
):
    """
    Build unique_filter and lookup_filter for field matching.

    Handles foreign key field detection and automatic _id suffix conversion for database lookups.

    Args:
        model_class: The Django model class
        unique_fields: List of field names that form the unique constraint
        validated_data: Validated data from serializer
        result: OperationResult object for error tracking
        index: Current item index for error reporting
        item_data: Original item data for error context

    Returns:
        tuple: (unique_filter, lookup_filter) dictionaries
    """
    unique_filter = {}
    lookup_filter = {}

    for field in unique_fields:
        if field in validated_data:
            unique_filter[field] = validated_data[field]
            
            # Handle both regular field names and *_id field names
            if field.endswith('_id'):
                # This is already a *_id field, use it directly for lookup
                lookup_filter[field] = validated_data[field]
            else:
                # This is a regular field name, check if it's a foreign key
                if hasattr(model_class, field):
                    field_obj = getattr(model_class, field)
                    if hasattr(field_obj, 'field'):
                        # This is a ForeignKey field, use _id suffix for lookup
                        lookup_filter[f"{field}_id"] = validated_data[field]
                    else:
                        # This is a regular field, use as-is
                        lookup_filter[field] = validated_data[field]
                else:
                    # Field doesn't exist on model, use as-is
                    lookup_filter[field] = validated_data[field]
        else:
            result.add_error(
                index, f"Missing required unique field: {field}", item_data
            )

    return unique_filter, lookup_filter


@shared_task(bind=True)
def async_create_task(
    self, serializer_class_path: str, data_list: list[dict], user_id: int | None = None
):
    """
    Celery task for async creation of model instances.

    Args:
        serializer_class_path: Full path to the serializer class
            (e.g., 'augend.financial_transactions.api.serializers.FinancialTransactionSerializer')
        data_list: List of dictionaries containing data for each instance
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id
    
    # Enhanced logging
    log_celery_task_start("async_create_task", task_id, 
                         serializer=serializer_class_path, 
                         item_count=len(data_list), 
                         user_id=user_id)
    
    log_bulk_operation_start("bulk_create", len(data_list), 
                            serializer=serializer_class_path)

    result = OperationResult(task_id, len(data_list), "async_create")

    # Initialize progress tracking in Redis
    OperationCache.set_task_progress(
        task_id, 0, len(data_list), "Starting async create..."
    )

    try:
        logger.debug(
            f"async_create_task - Importing serializer: {serializer_class_path}"
        )
        serializer_class = import_string(serializer_class_path)
        model_class = serializer_class.Meta.model
        logger.debug(f"async_create_task - Using model: {model_class.__name__}")
        instances_to_create = []

        # Validate all items first
        logger.debug(
            f"async_create_task - Starting validation of {len(data_list)} items"
        )
        OperationCache.set_task_progress(
            task_id, 0, len(data_list), "Validating data..."
        )

        for index, item_data in enumerate(data_list):
            try:
                serializer = serializer_class(data=item_data)
                if serializer.is_valid():
                    instances_to_create.append((index, serializer.validated_data))
                else:
                    # Log validation errors with stack trace for debugging
                    error_msg = f"Serializer validation failed at index {index}: {str(serializer.errors)}"
                    logger.error(f"async_create_task - {error_msg}")
                    logger.debug(
                        f"async_create_task - Validation error stack trace:\n{traceback.format_exc()}"
                    )
                    logger.exception(
                        "Serializer validation failed in async create task %s at index %s",
                        task_id,
                        index,
                    )
                    result.add_error(index, error_msg, item_data)
            except (ValidationError, ValueError) as e:
                # Log full stack trace for debugging
                error_msg = f"Validation error at index {index}: {str(e)}"
                logger.error(f"async_create_task - {error_msg}")
                logger.debug(
                    f"async_create_task - Stack trace:\n{traceback.format_exc()}"
                )
                logger.exception(
                    "Validation error in async create task %s at index %s",
                    task_id,
                    index,
                )
                result.add_error(index, error_msg, item_data)

            # Update progress every 10 items or at the end
            if (index + 1) % 10 == 0 or index == len(data_list) - 1:
                OperationCache.set_task_progress(
                    task_id,
                    index + 1,
                    len(data_list),
                    "Validated "
                    + str(index + 1)
                    + "/"
                    + str(len(data_list))
                    + " items",
                )

        # Create instances
        if instances_to_create:
            OperationCache.set_task_progress(
                task_id,
                len(data_list),
                len(data_list),
                "Creating instances...",
            )

            model_class = serializer_class.Meta.model

            # Handle foreign key fields properly by converting integer IDs to _id fields
            def prepare_model_data(validated_data):
                model_data = {}
                for field_name, value in validated_data.items():
                    # Check if this is a foreign key field that was overridden
                    if hasattr(model_class, field_name):
                        field = model_class._meta.get_field(field_name)
                        if hasattr(field, "related_model") and field.related_model:
                            # This is a foreign key field
                            # Extract the actual ID from the model instance if it's a model instance
                            if hasattr(value, "pk"):
                                # It's a model instance, extract the primary key
                                actual_value = value.pk
                            elif hasattr(value, "id"):
                                # It's a model instance, extract the id
                                actual_value = value.id
                            else:
                                # It's already an ID value (could be string or int)
                                actual_value = value

                            # Check if this is a SlugRelatedField (uses slug as primary key)
                            if hasattr(value, "_meta") and hasattr(value._meta, "pk"):
                                # Value is a model instance - check its primary key type
                                pk_field = value._meta.pk
                                if (
                                    hasattr(pk_field, "max_length")
                                    and pk_field.max_length is not None
                                    and pk_field.max_length > 0
                                ):
                                    # It's a CharField/SlugField primary key - don't use _id suffix
                                    model_data[field_name] = str(actual_value)
                                else:
                                    # It's an integer primary key - use _id suffix
                                    model_data[f"{field_name}_id"] = actual_value
                            else:
                                # Value is NOT a model instance (likely a string after field override)
                                # Check the related model's primary key type to determine if we need _id suffix
                                related_model = field.related_model
                                if related_model and hasattr(related_model._meta, "pk"):
                                    related_pk_field = related_model._meta.pk
                                    # Check if the related model uses string primary keys
                                    if (
                                        hasattr(related_pk_field, "max_length")
                                        and related_pk_field.max_length > 0
                                    ):
                                        # Related model uses string PK - don't use _id suffix
                                        model_data[field_name] = str(actual_value)
                                    else:
                                        # Related model uses integer PK - use _id suffix
                                        model_data[f"{field_name}_id"] = actual_value
                                else:
                                    # Default to _id suffix for foreign keys
                                    model_data[f"{field_name}_id"] = actual_value
                        else:
                            model_data[field_name] = value
                    else:
                        model_data[field_name] = value
                return model_data

            new_instances = [
                model_class(**prepare_model_data(validated_data))
                for _, validated_data in instances_to_create
            ]

            with transaction.atomic():
                created_instances = model_class.objects.bulk_create(new_instances)

                for instance in created_instances:
                    # Skip None instances that might be returned in some error cases
                    if instance is not None:
                        result.add_success(instance.id, "created")
                    else:
                        logger.warning(
                            "async_create_task - WARNING: bulk_create returned None instance"
                        )

        # Store final result in cache
        OperationCache.set_task_result(task_id, result.to_dict())

        # Enhanced completion logging
        log_bulk_operation_complete("bulk_create", result.success_count, result.error_count,
                                   task_id=task_id, serializer=serializer_class_path)
        
        log_celery_task_complete("async_create_task", task_id, True,
                               success_count=result.success_count, 
                               error_count=result.error_count)

        logger.debug(
            f"async_create_task - COMPLETED: success={result.success_count}, errors={result.error_count}"
        )
        logger.debug(f"async_create_task - Final result: {result.to_dict()}")

    except (ImportError, AttributeError) as e:
        logger.error(f"async_create_task - FATAL ERROR: {str(e)}")
        logger.error(
            f"async_create_task - Fatal error stack trace:\n{traceback.format_exc()}"
        )
        logger.exception("Async create task %s failed", task_id)
        result.add_error(0, f"Task failed: {e!s}")
        OperationCache.set_task_result(task_id, result.to_dict())

    return result.to_dict()


@shared_task(bind=True)
def async_update_task(
    self,
    serializer_class_path: str,
    updates_list: list[dict],
    user_id: int | None = None,
):
    """
    Celery task for async updating of model instances.

    Efficiently updates multiple instances using optimized database operations
    to reduce queries from N+1 to just 2 queries.

    Args:
        serializer_class_path: Full path to the serializer class
        updates_list: List of dictionaries containing id and update data for each instance
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id
    result = OperationResult(task_id, len(updates_list), "async_update")

    # Initialize progress tracking in Redis
    OperationCache.set_task_progress(
        task_id, 0, len(updates_list), "Starting async update..."
    )

    try:
        serializer_class = import_string(serializer_class_path)
        model_class = serializer_class.Meta.model

        # Extract all IDs for retrieval
        ids_to_update = [
            update_data.get("id")
            for update_data in updates_list
            if update_data.get("id")
        ]

        if not ids_to_update:
            result.add_error(0, "No valid IDs found in update data")
            OperationCache.set_task_result(task_id, result.to_dict())
            return result.to_dict()

        # Single query to fetch all instances
        OperationCache.set_task_progress(
            task_id, 0, len(updates_list), "Fetching instances..."
        )
        instances_dict = {
            instance.id: instance
            for instance in model_class.objects.filter(id__in=ids_to_update)
        }

        # Validate and prepare updates
        OperationCache.set_task_progress(
            task_id, 0, len(updates_list), "Validating updates..."
        )
        valid_updates = []
        fields_to_update = set()

        for index, update_data in enumerate(updates_list):
            try:
                instance_id = update_data.get("id")
                if not instance_id:
                    result.add_error(index, "Missing 'id' field", update_data)
                    continue

                instance = instances_dict.get(instance_id)
                if not instance:
                    result.add_error(
                        index, f"Instance with id {instance_id} not found", update_data
                    )
                    continue

                serializer = serializer_class(instance, data=update_data, partial=True)
                if serializer.is_valid():
                    # Update instance with validated data
                    for field, value in serializer.validated_data.items():
                        setattr(instance, field, value)
                        fields_to_update.add(field)

                    valid_updates.append((index, instance, instance_id))
                else:
                    # Log validation errors with stack trace for debugging
                    error_msg = f"Serializer validation failed at index {index}: {str(serializer.errors)}"
                    logger.error(f"async_update_task - {error_msg}")
                    logger.debug(
                        f"async_update_task - Validation error stack trace:\n{traceback.format_exc()}"
                    )
                    logger.exception(
                        "Serializer validation failed in async update task %s at index %s",
                        task_id,
                        index,
                    )
                    result.add_error(index, error_msg, update_data)

            except (ValidationError, ValueError) as e:
                # Log full stack trace for debugging
                error_msg = f"Validation error at index {index}: {str(e)}"
                logger.error(f"async_update_task - {error_msg}")
                logger.debug(
                    f"async_update_task - Stack trace:\n{traceback.format_exc()}"
                )
                logger.exception(
                    "Validation error in async update task %s at index %s",
                    task_id,
                    index,
                )
                result.add_error(index, error_msg, update_data)

            # Update progress every 10 items
            if (index + 1) % 10 == 0 or index == len(updates_list) - 1:
                OperationCache.set_task_progress(
                    task_id,
                    index + 1,
                    len(updates_list),
                    f"Validated {index + 1}/{len(updates_list)} items",
                )

        # Single bulk_update query for all valid instances
        if valid_updates:
            OperationCache.set_task_progress(
                task_id,
                len(updates_list),
                len(updates_list),
                "Performing async update...",
            )

            instances_to_update = [instance for _, instance, _ in valid_updates]
            fields_list = list(fields_to_update)

            with transaction.atomic():
                # Single query to update all instances
                model_class.objects.bulk_update(
                    instances_to_update,
                    fields_list,
                    batch_size=1000,  # Process in batches for very large updates
                )

                # Mark successful updates
                for _, instance, instance_id in valid_updates:
                    result.add_success(instance_id, "updated")

        # Store final result in cache
        OperationCache.set_task_result(task_id, result.to_dict())

        logger.debug(
            "Async update task %s completed: %s updated, %s errors",
            task_id,
            result.success_count,
            result.error_count,
        )

    except (ImportError, AttributeError) as e:
        logger.error(
            f"async_update_task - Fatal error stack trace:\n{traceback.format_exc()}"
        )
        logger.exception("Async update task %s failed", task_id)
        result.add_error(0, f"Task failed: {e!s}")
        OperationCache.set_task_result(task_id, result.to_dict())

    return result.to_dict()


@shared_task(bind=True)
def async_replace_task(
    self,
    serializer_class_path: str,
    replacements_list: list[dict],
    user_id: int | None = None,
):
    """
    Celery task for async replacement (full update) of model instances.

    Args:
        serializer_class_path: Full path to the serializer class
        replacements_list: List of dictionaries containing complete object data
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id
    result = OperationResult(task_id, len(replacements_list), "async_replace")

    # Initialize progress tracking in Redis
    OperationCache.set_task_progress(
        task_id, 0, len(replacements_list), "Starting async replace..."
    )

    try:
        serializer_class = import_string(serializer_class_path)
        model_class = serializer_class.Meta.model

        # Extract all IDs for retrieval
        ids_to_replace = [
            replacement_data.get("id")
            for replacement_data in replacements_list
            if replacement_data.get("id")
        ]

        if not ids_to_replace:
            result.add_error(0, "No valid IDs found in replacement data")
            OperationCache.set_task_result(task_id, result.to_dict())
            return result.to_dict()

        # Single query to fetch all instances
        OperationCache.set_task_progress(
            task_id, 0, len(replacements_list), "Fetching instances..."
        )
        instances_dict = {
            instance.id: instance
            for instance in model_class.objects.filter(id__in=ids_to_replace)
        }

        # Validate and prepare replacements
        OperationCache.set_task_progress(
            task_id, 0, len(replacements_list), "Validating replacements..."
        )
        valid_replacements = []
        all_fields = set()

        for index, replacement_data in enumerate(replacements_list):
            try:
                instance_id = replacement_data.get("id")
                if not instance_id:
                    result.add_error(index, "Missing 'id' field", replacement_data)
                    continue

                instance = instances_dict.get(instance_id)
                if not instance:
                    result.add_error(
                        index,
                        f"Instance with id {instance_id} not found",
                        replacement_data,
                    )
                    continue

                serializer = serializer_class(instance, data=replacement_data)
                if serializer.is_valid():
                    # Replace instance with validated data
                    for field, value in serializer.validated_data.items():
                        setattr(instance, field, value)
                        all_fields.add(field)

                    valid_replacements.append((index, instance, instance_id))
                else:
                    # Log validation errors with stack trace for debugging
                    error_msg = f"Serializer validation failed at index {index}: {str(serializer.errors)}"
                    logger.error(f"async_replace_task - {error_msg}")
                    logger.debug(
                        f"async_replace_task - Validation error stack trace:\n{traceback.format_exc()}"
                    )
                    logger.exception(
                        "Serializer validation failed in async replace task %s at index %s",
                        task_id,
                        index,
                    )
                    result.add_error(index, error_msg, replacement_data)

            except (ValidationError, ValueError) as e:
                # Log full stack trace for debugging
                error_msg = f"Validation error at index {index}: {str(e)}"
                logger.error(f"async_replace_task - {error_msg}")
                logger.debug(
                    f"async_replace_task - Stack trace:\n{traceback.format_exc()}"
                )
                logger.exception(
                    "Validation error in async replace task %s at index %s",
                    task_id,
                    index,
                )
                result.add_error(index, error_msg, replacement_data)

            # Update progress every 10 items
            if (index + 1) % 10 == 0 or index == len(replacements_list) - 1:
                OperationCache.set_task_progress(
                    task_id,
                    index + 1,
                    len(replacements_list),
                    f"Validated {index + 1}/{len(replacements_list)} items",
                )

        # Single bulk_update query for all valid instances
        if valid_replacements:
            OperationCache.set_task_progress(
                task_id,
                len(replacements_list),
                len(replacements_list),
                "Performing async replace...",
            )

            instances_to_replace = [instance for _, instance, _ in valid_replacements]
            fields_list = list(all_fields)

            with transaction.atomic():
                # Single query to replace all instances
                model_class.objects.bulk_update(
                    instances_to_replace, fields_list, batch_size=1000
                )

                # Mark successful replacements
                for _, instance, instance_id in valid_replacements:
                    result.add_success(instance_id, "updated")

        # Store final result in cache
        OperationCache.set_task_result(task_id, result.to_dict())

        logger.debug(
            "Async replace task %s completed: %s replaced, %s errors",
            task_id,
            result.success_count,
            result.error_count,
        )

    except (ImportError, AttributeError) as e:
        logger.error(
            f"async_replace_task - Fatal error stack trace:\n{traceback.format_exc()}"
        )
        logger.exception("Async replace task %s failed", task_id)
        result.add_error(0, f"Task failed: {e!s}")
        OperationCache.set_task_result(task_id, result.to_dict())

    return result.to_dict()


@shared_task(bind=True)
def async_delete_task(
    self, model_class_path: str, ids_list: list[int], user_id: int | None = None
):
    """
    Celery task for async deletion of model instances.

    Args:
        model_class_path: Full path to the model class
        ids_list: List of IDs to delete
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id
    result = OperationResult(task_id, len(ids_list), "async_delete")

    # Initialize progress tracking in Redis
    OperationCache.set_task_progress(
        task_id, 0, len(ids_list), "Starting async delete..."
    )

    try:
        model_class = import_string(model_class_path)

        OperationCache.set_task_progress(
            task_id, 0, len(ids_list), "Deleting instances..."
        )

        with transaction.atomic():
            # Use optimized delete operation for efficiency
            deleted_count, _ = model_class.objects.filter(id__in=ids_list).delete()

            # Mark successful deletions
            for item_id in ids_list:
                result.add_success(item_id, "deleted")

        # Store final result in cache
        OperationCache.set_task_result(task_id, result.to_dict())

        logger.debug(
            "Async delete task %s completed: %s deleted",
            task_id,
            deleted_count,
        )

    except (ImportError, AttributeError) as e:
        logger.error(
            f"async_delete_task - Fatal error stack trace:\n{traceback.format_exc()}"
        )
        logger.exception("Async delete task %s failed", task_id)
        result.add_error(0, f"Task failed: {e!s}")
        OperationCache.set_task_result(task_id, result.to_dict())

    return result.to_dict()


@shared_task(bind=True)
def async_get_task(
    self,
    model_class_path: str,
    serializer_class_path: str,
    query_data: dict,
    user_id: int | None = None,
):
    """
    Celery task for async retrieval of model instances.

    Args:
        model_class_path: Full path to the model class
        serializer_class_path: Full path to the serializer class
        query_data: Dictionary containing query parameters
        user_id: Optional user ID for audit purposes
    """
    task_id = self.request.id

    # Initialize progress tracking in Redis
    OperationCache.set_task_progress(task_id, 0, 1, "Starting async get...")

    try:
        model_class = import_string(model_class_path)
        serializer_class = import_string(serializer_class_path)

        OperationCache.set_task_progress(task_id, 0, 1, "Executing query...")

        # Handle different query types
        if "ids" in query_data:
            # ID-based retrieval
            ids_list = query_data["ids"]
            queryset = model_class.objects.filter(id__in=ids_list)
        elif "filters" in query_data:
            # Complex filter-based retrieval
            filters = query_data["filters"]
            queryset = model_class.objects.filter(**filters)
        else:
            # Default queryset
            queryset = model_class.objects.all()

        # Serialize the results
        OperationCache.set_task_progress(task_id, 1, 1, "Serializing results...")
        serializer = serializer_class(queryset, many=True)
        serialized_data = serializer.data

        # Store final result in cache
        result = {
            "task_id": task_id,
            "operation_type": "async_get",
            "count": len(serialized_data),
            "results": serialized_data,
            "success": True,
        }
        OperationCache.set_task_result(task_id, result)

        logger.debug(
            "Async get task %s completed: %s records retrieved",
            task_id,
            len(serialized_data),
        )

        return result

    except (ImportError, AttributeError) as e:
        logger.error(
            f"async_get_task - Fatal error stack trace:\n{traceback.format_exc()}"
        )
        logger.exception("Async get task %s failed", task_id)
        error_result = {
            "task_id": task_id,
            "operation_type": "async_get",
            "error": f"Task failed: {e!s}",
            "success": False,
        }
        OperationCache.set_task_result(task_id, error_result)
        return error_result


@shared_task(bind=True)
def async_upsert_task(
    self,
    serializer_class_path: str,
    data_list: list[dict],
    unique_fields: list[str],
    update_fields: list[str] | None = None,
    user_id: int | None = None,
    upsert_context: dict | None = None,
):
    """
    Celery task for async upsert (insert or update) of model instances.

    Intelligent upsert operation that creates new records or updates existing ones
    based on unique field constraints.

    Args:
        serializer_class_path: Full path to the serializer class
        data_list: List of dictionaries containing data for each instance
        unique_fields: List of field names that form the unique constraint
        update_fields: List of field names to update on conflict (if None, updates all fields)
        user_id: Optional user ID for audit purposes
    """
    import time
    start_time = time.time()
    
    # Enhanced timing logging
    logger.debug("=== CELERY UPSERT TASK STARTED ===")
    logger.debug(f"Task ID: {self.request.id}")
    logger.debug(f"Items to process: {len(data_list)}")
    logger.debug(f"Serializer: {serializer_class_path}")
    logger.debug(f"Unique fields: {unique_fields}")
    logger.debug(f"Update fields: {update_fields}")
    logger.debug(f"Upsert context: {upsert_context}")
    logger.debug(f"User ID: {user_id}")
    logger.debug("==================================")

    task_id = self.request.id
    result = OperationResult(task_id, len(data_list), "async_upsert")

    # Initialize progress tracking in Redis
    OperationCache.set_task_progress(
        task_id, 0, len(data_list), "Starting async upsert..."
    )

    try:
        # Phase 1: Import and Setup
        phase_start = time.time()
        logger.debug("PHASE 1: Import and Setup")
        
        import_start = time.time()
        logger.debug(f"Importing serializer: {serializer_class_path}")
        serializer_class = import_string(serializer_class_path)
        model_class = serializer_class.Meta.model
        logger.debug(f"Using model: {model_class.__name__}")
        import_time = time.time() - import_start
        logger.debug(f"Import completed in {import_time:.4f}s")
        
        phase1_time = time.time() - phase_start
        logger.debug(f"PHASE 1 TOTAL: {phase1_time:.4f}s")

        # Handle upsert context for skipping uniqueness validation
        skip_uniqueness = upsert_context and upsert_context.get(
            "skip_uniqueness_validation", False
        )
        if skip_uniqueness:
            logger.debug(
                "async_upsert_task - UPSERT MODE: Skipping uniqueness validation for upsert operation"
            )
            # We'll handle uniqueness at the database level, not serializer level
            # The serializer validators will be filtered during validation
        instances_to_create = []
        instances_to_update = []

        # Phase 2: Data Validation
        phase_start = time.time()
        logger.debug("PHASE 2: Data Validation")
        
        validation_start = time.time()
        logger.debug(f"Starting validation of {len(data_list)} items")
        OperationCache.set_task_progress(
            task_id, 0, len(data_list), "Validating data..."
        )

        for index, item_data in enumerate(data_list):
            try:
                # Fix field mapping issues - convert financial_account_id to financial_account if needed
                processed_data = item_data.copy()
                if 'financial_account_id' in processed_data and 'financial_account' not in processed_data:
                    processed_data['financial_account'] = processed_data['financial_account_id']
                
                # Create serializer with upsert validation bypass
                if skip_uniqueness:
                    logger.debug(
                        f"async_upsert_task - Creating upsert-aware serializer for item {index}"
                    )

                    # Create a custom serializer class that bypasses model validation for upsert
                    class UpsertSerializer(serializer_class):
                        def __init__(self, *args, **kwargs):
                            super().__init__(*args, **kwargs)
                            # Remove all uniqueness-related validators from serializer level
                            original_validators = self.validators[:]
                            self.validators = [
                                v
                                for v in self.validators
                                if not self._is_uniqueness_validator(v, unique_fields)
                            ]
                            logger.debug(
                                f"async_upsert_task - Filtered validators: {len(original_validators)} -> {len(self.validators)}"
                            )

                            # Debug: Print field types for unique fields and override problematic fields
                            for field_name in unique_fields:
                                if field_name in self.fields:
                                    field = self.fields[field_name]
                                    field_type_name = type(field).__name__
                                    logger.debug(
                                        f"async_upsert_task - Field '{field_name}' type: {field_type_name}"
                                    )

                                    # If the field is a PrimaryKeyRelatedField or similar foreign key field,
                                    # we need to override it for upsert operations
                                    # This handles cases where fields are incorrectly configured as foreign keys
                                    if (
                                        hasattr(field, "queryset")
                                        or "RelatedField" in field_type_name
                                    ):
                                        from rest_framework import serializers

                                        # Determine the appropriate field type based on the related field type
                                        if "SlugRelatedField" in field_type_name:
                                            # SlugRelatedField should be overridden to CharField
                                            self.fields[field_name] = (
                                                serializers.CharField()
                                            )
                                            logger.debug(
                                                f"async_upsert_task - Overriding field '{field_name}' from {field_type_name} to CharField for upsert"
                                            )
                                        else:
                                            # Other related fields should be overridden to IntegerField
                                            self.fields[field_name] = (
                                                serializers.IntegerField()
                                            )
                                            logger.debug(
                                                f"async_upsert_task - Overriding field '{field_name}' from {field_type_name} to IntegerField for upsert"
                                            )
                                    else:
                                        logger.debug(
                                            f"async_upsert_task - Field '{field_name}' not overridden (type: {field_type_name}, has_queryset: {hasattr(field, 'queryset')})"
                                        )

                            # Also remove uniqueness validators from individual fields and override validation
                            for field_name, field in self.fields.items():
                                if field_name in unique_fields:
                                    # Remove validators
                                    if hasattr(field, "validators"):
                                        original_field_validators = field.validators[:]
                                        field.validators = [
                                            v
                                            for v in field.validators
                                            if not self._is_field_uniqueness_validator(
                                                v, field_name
                                            )
                                        ]
                                        if len(original_field_validators) != len(
                                            field.validators
                                        ):
                                            logger.debug(
                                                f"async_upsert_task - Removed {len(original_field_validators) - len(field.validators)} uniqueness validators from field '{field_name}'"
                                            )

                                    # Override field validation to bypass uniqueness checks
                                    original_run_validation = field.run_validation

                                    def bypass_uniqueness_validation(data):
                                        try:
                                            return original_run_validation(data)
                                        except Exception as e:
                                            # If it's a uniqueness error or a "does not exist" error for unique fields, suppress it
                                            error_str = str(e).lower()
                                            if (
                                                "unique" in error_str
                                                and "already exists" in error_str
                                            ) or ("does not exist" in error_str):
                                                logger.debug(
                                                    f"async_upsert_task - Suppressing validation error for field '{field_name}': {e}"
                                                )
                                                # Return the data as-is for upsert processing
                                                return data
                                            else:
                                                # Re-raise non-uniqueness errors
                                                raise e

                                    field.run_validation = bypass_uniqueness_validation

                        def _is_uniqueness_validator(self, validator, unique_fields):
                            """Check if validator is related to uniqueness constraints."""
                            # Check for UniqueTogetherValidator
                            if hasattr(validator, "fields") and hasattr(
                                validator, "queryset"
                            ):
                                validator_fields = getattr(validator, "fields", [])
                                return any(
                                    field in unique_fields for field in validator_fields
                                )

                            # Check for UniqueValidator (field-level uniqueness)
                            if hasattr(validator, "queryset") and hasattr(
                                validator, "field_name"
                            ):
                                return validator.field_name in unique_fields

                            # Check for UniqueValidator by class name
                            validator_class_name = validator.__class__.__name__
                            if validator_class_name == "UniqueValidator":
                                # For UniqueValidator, we need to check if it's validating one of our unique fields
                                # This is a bit tricky since we don't have direct access to the field name
                                # We'll be more permissive and assume it could be a uniqueness validator
                                return True

                            return False

                        def _is_field_uniqueness_validator(self, validator, field_name):
                            """Check if a field validator is a uniqueness validator for the specified field."""
                            validator_class_name = validator.__class__.__name__

                            # Check for UniqueValidator
                            if validator_class_name == "UniqueValidator":
                                return True

                            # Check for other uniqueness-related validators
                            if hasattr(validator, "queryset") and hasattr(
                                validator, "field_name"
                            ):
                                return validator.field_name == field_name

                            return False

                        def is_valid(self, raise_exception=False):
                            # Call parent validation but skip model-level validation
                            result = super().is_valid(raise_exception=raise_exception)

                            # If validation failed due to uniqueness, clear those errors
                            if not result and "non_field_errors" in self.errors:
                                filtered_errors = []
                                for error in self.errors["non_field_errors"]:
                                    error_str = str(error).lower()
                                    if (
                                        "unique" in error_str
                                        and "must make a unique set" in error_str
                                    ):
                                        logger.debug(
                                            f"async_upsert_task - Suppressing uniqueness error: {error}"
                                        )
                                        continue
                                    filtered_errors.append(error)

                                if filtered_errors:
                                    self.errors["non_field_errors"] = filtered_errors
                                else:
                                    del self.errors["non_field_errors"]

                                # Recalculate validation result
                                result = not bool(self.errors)

                            return result

                    serializer = UpsertSerializer(data=processed_data)
                else:
                    serializer = serializer_class(data=processed_data)

                if serializer.is_valid():
                    validated_data = serializer.validated_data

                    # Check if record exists based on unique fields
                    unique_filter, lookup_filter = _build_field_filters(
                        model_class,
                        unique_fields,
                        validated_data,
                        result,
                        index,
                        item_data,
                    )
                    if not unique_filter:
                        continue

                    # Try to find existing instance
                    existing_instance = model_class.objects.filter(
                        **lookup_filter
                    ).first()

                    if existing_instance:
                        # Update existing instance
                        if update_fields:
                            # Only update specified fields
                            update_data = {
                                k: v
                                for k, v in validated_data.items()
                                if k in update_fields
                            }
                        else:
                            # Update all fields except unique fields
                            update_data = {
                                k: v
                                for k, v in validated_data.items()
                                if k not in unique_fields
                            }

                        # Update the instance
                        for field, value in update_data.items():
                            setattr(existing_instance, field, value)

                        instances_to_update.append(
                            (index, existing_instance, existing_instance.id)
                        )
                    else:
                        # Create new instance
                        # Handle foreign key fields properly by converting integer IDs to _id fields
                        model_data = {}
                        for field_name, value in validated_data.items():
                            # Check if this is a foreign key field that was overridden
                            if hasattr(model_class, field_name):
                                field = model_class._meta.get_field(field_name)
                                if (
                                    hasattr(field, "related_model")
                                    and field.related_model
                                ):
                                    # This is a foreign key field
                                    # Extract the actual ID from the model instance if it's a model instance
                                    if hasattr(value, "pk"):
                                        # It's a model instance, extract the primary key
                                        actual_value = value.pk
                                    elif hasattr(value, "id"):
                                        # It's a model instance, extract the id
                                        actual_value = value.id
                                    else:
                                        # It's already an ID value (could be string or int)
                                        actual_value = value

                                    # Check if this is a SlugRelatedField (uses slug as primary key)
                                    if hasattr(value, "_meta") and hasattr(
                                        value._meta, "pk"
                                    ):
                                        # Value is a model instance - check its primary key type
                                        pk_field = value._meta.pk
                                        if (
                                            hasattr(pk_field, "max_length")
                                            and pk_field.max_length is not None
                                            and pk_field.max_length > 0
                                        ):
                                            # It's a CharField/SlugField primary key - don't use _id suffix
                                            model_data[field_name] = str(actual_value)
                                        else:
                                            # It's an integer primary key - use _id suffix
                                            model_data[f"{field_name}_id"] = (
                                                actual_value
                                            )
                                    else:
                                        # Value is NOT a model instance (likely a string after field override)
                                        # Check the related model's primary key type to determine if we need _id suffix
                                        related_model = field.related_model
                                        if related_model and hasattr(
                                            related_model._meta, "pk"
                                        ):
                                            related_pk_field = related_model._meta.pk
                                            # Check if the related model uses string primary keys
                                            if (
                                                hasattr(related_pk_field, "max_length")
                                                and related_pk_field.max_length
                                                is not None
                                                and related_pk_field.max_length > 0
                                            ):
                                                # Related model uses string PK - don't use _id suffix
                                                model_data[field_name] = str(
                                                    actual_value
                                                )
                                            else:
                                                # Related model uses integer PK - use _id suffix
                                                model_data[f"{field_name}_id"] = (
                                                    actual_value
                                                )
                                        else:
                                            # Default to _id suffix for foreign keys
                                            model_data[f"{field_name}_id"] = (
                                                actual_value
                                            )
                                else:
                                    model_data[field_name] = value
                            else:
                                model_data[field_name] = value

                        instance = model_class(**model_data)
                        instances_to_create.append((index, instance))
                else:
                    # Log validation errors with stack trace for debugging
                    error_msg = f"Serializer validation failed at index {index}: {str(serializer.errors)}"
                    logger.error(f"async_upsert_task - {error_msg}")
                    logger.debug(
                        f"async_upsert_task - Validation error stack trace:\n{traceback.format_exc()}"
                    )
                    logger.exception(
                        "Serializer validation failed in async upsert task %s at index %s",
                        task_id,
                        index,
                    )
                    result.add_error(index, error_msg, item_data)
            except (ValidationError, ValueError) as e:
                # Log full stack trace for debugging
                error_msg = f"Validation error at index {index}: {str(e)}"
                logger.error(f"async_upsert_task - {error_msg}")
                logger.debug(
                    f"async_upsert_task - Stack trace:\n{traceback.format_exc()}"
                )
                logger.exception(
                    "Validation error in async upsert task %s at index %s",
                    task_id,
                    index,
                )
                result.add_error(index, error_msg, item_data)

            # Update progress every 10 items or at the end
            if (index + 1) % 10 == 0 or index == len(data_list) - 1:
                OperationCache.set_task_progress(
                    task_id,
                    index + 1,
                    len(data_list),
                    "Validated "
                    + str(index + 1)
                    + "/"
                    + str(len(data_list))
                    + " items",
                )

        validation_time = time.time() - validation_start
        phase2_time = time.time() - phase_start
        logger.debug(f"Validation completed in {validation_time:.4f}s for {len(data_list)} items")
        logger.debug(f"PHASE 2 TOTAL: {phase2_time:.4f}s")
        logger.debug(f"Validation rate: {len(data_list)/validation_time:.2f} items/second")

        # Phase 3: Database Operations
        phase_start = time.time()
        logger.debug("PHASE 3: Database Operations")
        
        bulk_operation_start = time.time()
        bulk_operation_time = 0.0

        # Perform true upsert using bulk_create with update_conflicts
        if instances_to_create or instances_to_update:
            logger.debug(f"Preparing upsert: create={len(instances_to_create)}, update={len(instances_to_update)}")
            OperationCache.set_task_progress(
                task_id,
                len(data_list),
                len(data_list),
                "Performing upsert...",
            )

            try:
                with transaction.atomic():
                    # Prepare all instances for upsert
                    all_instances = []
                    logger.debug(f"Preparing {len(instances_to_create) + len(instances_to_update)} instances for bulk operation")

                    # Add instances to create
                    for _, instance in instances_to_create:
                        all_instances.append(instance)

                    # Add instances to update
                    for _, instance, _ in instances_to_update:
                        all_instances.append(instance)

                    if all_instances:
                        # Determine fields to update on conflict
                        if update_fields:
                            fields_to_update = update_fields
                            logger.debug(
                                "async_upsert_task - Using provided update_fields: "
                                + str(fields_to_update)
                            )
                        else:
                            # Auto-determine update fields (all non-unique fields, excluding auto-set fields)
                            if all_instances:
                                first_instance = all_instances[0]
                                fields_to_update = [
                                    field.name
                                    for field in first_instance._meta.fields
                                    if field.name not in unique_fields
                                    and not field.primary_key
                                    and not getattr(field, "auto_now", False)
                                    and not getattr(field, "auto_now_add", False)
                                ]
                            logger.debug(
                                "async_upsert_task - Auto-determined update_fields: "
                                + str(fields_to_update)
                            )

                        # Perform true upsert with unique constraint
                        if fields_to_update:
                            logger.debug("Executing bulk_create with update_conflicts")
                            logger.debug(f"unique_fields: {unique_fields}")
                            logger.debug(f"update_fields: {fields_to_update}")
                            logger.debug("batch_size: 1000")

                            db_exec_start = time.time()
                            try:
                                created_instances = model_class.objects.bulk_create(
                                    all_instances,
                                    update_conflicts=True,
                                    update_fields=fields_to_update,
                                    unique_fields=unique_fields,
                                    batch_size=1000,
                                )
                                db_exec_time = time.time() - db_exec_start
                                logger.debug(f"Database bulk_create completed in {db_exec_time:.4f}s")

                                if created_instances:
                                    logger.debug(f"bulk_create completed, returned {len(created_instances)} instances")

                                    # Mark all as successful (both created and updated)
                                    for instance in created_instances:
                                        # Note: bulk_create with update_conflicts returns all instances
                                        # We can't distinguish created vs updated without additional queries
                                        # Skip None instances that might be returned in some error cases
                                        if instance is not None:
                                            result.add_success(instance.id, "updated")
                                        else:
                                            logger.warning(
                                                "async_upsert_task - WARNING: bulk_create returned None instance"
                                            )
                                else:
                                    logger.warning(
                                        "async_upsert_task - bulk_create returned no instances"
                                    )
                                    result.add_error(
                                        0, "Bulk create operation returned no instances"
                                    )
                            except Exception as bulk_error:
                                logger.error(
                                    "async_upsert_task - bulk_create failed: "
                                    + str(bulk_error)
                                )
                                logger.error(
                                    f"async_upsert_task - Bulk create error stack trace:\n{traceback.format_exc()}"
                                )
                                logger.exception(
                                    "Bulk create error in async upsert task %s", task_id
                                )
                                result.add_error(
                                    0, "Bulk upsert failed: " + str(bulk_error)
                                )
                                created_instances = []
                        else:
                            logger.debug(
                                "async_upsert_task - No update fields, using separate operations"
                            )
                            # Fallback to separate operations if no update fields
                            try:
                                created_instances = model_class.objects.bulk_create(
                                    [instance for _, instance in instances_to_create]
                                )
                                if created_instances:
                                    for instance in created_instances:
                                        # Skip None instances that might be returned in some error cases
                                        if instance is not None:
                                            result.add_success(instance.id, "created")
                                        else:
                                            logger.warning(
                                                "async_upsert_task - WARNING: bulk_create (fallback) returned None instance"
                                            )

                                # Update existing instances
                                update_instances = [
                                    instance for _, instance, _ in instances_to_update
                                ]
                                if update_instances and fields_to_update:
                                    model_class.objects.bulk_update(
                                        update_instances,
                                        fields_to_update,
                                        batch_size=1000,
                                    )
                                    for _, instance, instance_id in instances_to_update:
                                        result.add_success(instance_id, "updated")
                            except Exception as fallback_error:
                                logger.error(
                                    "async_upsert_task - Fallback operations failed: "
                                    + str(fallback_error)
                                )
                                result.add_error(
                                    0,
                                    "Fallback upsert operations failed: "
                                    + str(fallback_error),
                                )
                                created_instances = []

            except Exception as e:
                logger.error(
                    "async_upsert_task - ERROR during bulk operation: " + str(e)
                )
                logger.error(
                    f"async_upsert_task - Bulk operation error stack trace:\n{traceback.format_exc()}"
                )
                logger.exception(
                    "Bulk operation error in async upsert task %s", task_id
                )
                # Handle unique constraint errors specifically
                error_msg = str(e)
                if (
                    "unique constraint" in error_msg.lower()
                    or "unique_fields" in error_msg.lower()
                ):
                    result.add_error(
                        0,
                        "Unique constraint error: " + error_msg + ". "
                        "Ensure fields "
                        + str(unique_fields)
                        + " form a unique constraint in your database.",
                    )
                else:
                    result.add_error(0, "Upsert failed: " + error_msg)
            
            # Calculate bulk operation time
            bulk_operation_time = time.time() - bulk_operation_start
            phase3_time = time.time() - phase_start
            logger.debug(f"Bulk operation completed in {bulk_operation_time:.4f}s")
            logger.debug(f"PHASE 3 TOTAL: {phase3_time:.4f}s")
        else:
            # No instances to process, bulk operation time is 0
            bulk_operation_time = 0.0
            phase3_time = time.time() - phase_start
            logger.debug("No instances to process")
            logger.debug(f"PHASE 3 TOTAL: {phase3_time:.4f}s")

        # Store final result in cache
        OperationCache.set_task_result(task_id, result.to_dict())

        # Phase 4: Finalization and Summary
        phase_start = time.time()
        logger.debug("PHASE 4: Finalization")
        
        # Store final result in cache
        OperationCache.set_task_result(task_id, result.to_dict())
        
        phase4_time = time.time() - phase_start
        logger.debug(f"PHASE 4 TOTAL: {phase4_time:.4f}s")

        # Comprehensive timing summary
        total_time = time.time() - start_time
        
        # Store timing info in result for main application to see
        result.timing_info = {
            "total_time": total_time,
            "phase1_time": phase1_time,
            "phase2_time": phase2_time,
            "phase3_time": phase3_time,
            "phase4_time": phase4_time,
            "processing_rate": len(data_list)/total_time,
            "phase1_percent": phase1_time/total_time*100,
            "phase2_percent": phase2_time/total_time*100,
            "phase3_percent": phase3_time/total_time*100,
            "phase4_percent": phase4_time/total_time*100,
        }
        
        logger.debug("=== CELERY UPSERT TASK COMPLETED ===")
        logger.debug(f"TOTAL TIME: {total_time:.4f}s")
        logger.debug("TIMING BREAKDOWN:")
        logger.debug(f"  - Phase 1 (Import/Setup): {phase1_time:.4f}s ({phase1_time/total_time*100:.1f}%)")
        logger.debug(f"  - Phase 2 (Validation): {phase2_time:.4f}s ({phase2_time/total_time*100:.1f}%)")
        logger.debug(f"  - Phase 3 (Database): {phase3_time:.4f}s ({phase3_time/total_time*100:.1f}%)")
        logger.debug(f"  - Phase 4 (Finalization): {phase4_time:.4f}s ({phase4_time/total_time*100:.1f}%)")
        logger.debug(f"  - TOTAL: {total_time:.4f}s")
        logger.debug(f"Processing rate: {len(data_list)/total_time:.2f} items/second")
        logger.debug(f"Results: success={result.success_count}, errors={result.error_count}")
        logger.debug("=====================================")

        logger.debug(
            "Async upsert task %s completed: %s created, %s updated, %s errors",
            task_id,
            len([op for op in result.created_ids]),
            len([op for op in result.updated_ids]),
            result.error_count,
        )

    except (ImportError, AttributeError) as e:
        logger.error("async_upsert_task - FATAL ERROR: " + str(e))
        logger.error(
            f"async_upsert_task - Fatal error stack trace:\n{traceback.format_exc()}"
        )
        logger.exception("Async upsert task %s failed", task_id)
        result.add_error(0, "Task failed: " + str(e))
        OperationCache.set_task_result(task_id, result.to_dict())

    return result.to_dict()
