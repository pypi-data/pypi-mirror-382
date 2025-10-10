import logging
from django.db.models import ForeignKey
from rest_framework import serializers

logger = logging.getLogger(__name__)


class BulkModelSerializer(serializers.ModelSerializer):
    """
    Bulk-optimized serializer that accepts standard Django field names and converts
    them internally for optimal bulk operation performance.

    Key features:
    - Accepts standard field names (loan_account) in API requests
    - Converts to *_id fields internally for bulk_create/bulk_update efficiency
    - Returns standard field names in responses for consistency
    - Full django-filter compatibility
    - Avoids foreign key validation queries during bulk operations
    """

    def get_fields(self):
        """Add *_id fields to the serializer for bulk operations."""
        fields = super().get_fields()
        
        # Add *_id fields for all ForeignKey relationships
        for model_field in self.Meta.model._meta.get_fields():
            if not isinstance(model_field, ForeignKey):
                continue

            fk_name = model_field.name  # e.g., 'business'
            fk_attname = model_field.attname  # e.g., 'business_id'

            # Check if this field is a SlugRelatedField - if so, skip adding *_id field
            if fk_name in fields:
                serializer_field = fields[fk_name]
                if isinstance(serializer_field, serializers.SlugRelatedField):
                    logger.debug(f"BulkModelSerializer - Skipping *_id field creation for SlugRelatedField '{fk_name}'")
                    continue

            # Add the *_id field if it's not already defined
            if fk_attname not in fields:
                fields[fk_attname] = serializers.IntegerField(
                    required=False,  # Make it optional since we convert from the standard field
                    allow_null=model_field.null,
                    write_only=True,  # Only for input, not output
                )
                logger.debug(f"BulkModelSerializer - Added field '{fk_attname}' for FK '{fk_name}'")

            # Make the original FK field not required since we'll convert to *_id
            # But only if it's not a SlugRelatedField (those stay required as they are)
            if fk_name in fields:
                original_field = fields[fk_name]
                if not isinstance(original_field, serializers.SlugRelatedField):
                    # Simply modify the existing field's required attribute instead of recreating it
                    if hasattr(original_field, 'required'):
                        logger.debug(f"BulkModelSerializer - Field '{fk_name}' required BEFORE: {original_field.required}")
                        original_field.required = False
                        logger.debug(f"BulkModelSerializer - Field '{fk_name}' required AFTER: {original_field.required}")
                        logger.debug(f"BulkModelSerializer - Made field '{fk_name}' not required (has {fk_attname} alternative)")

        return fields

    def to_internal_value(self, data):
        """
        Convert standard foreign key field names to *_id fields for bulk operations.

        Example:
        Input:  {"loan_account": 123, "amount": 1000}
        Output: {"loan_account_id": 123, "amount": 1000}

        This allows users to work with familiar Django field names while optimizing
        the internal representation for bulk database operations.
        
        Note: SlugRelatedFields are NOT converted to *_id fields since they expect
        the slug value, not the primary key ID.
        """
        # Make a copy to avoid modifying the original data
        internal_data = data.copy() if hasattr(data, "copy") else dict(data)

        model = self.Meta.model
        current_fields = self.get_fields()

        # Process all foreign key fields
        for model_field in model._meta.get_fields():
            if not isinstance(model_field, ForeignKey):
                continue

            fk_name = model_field.name  # e.g., 'business'
            fk_attname = model_field.attname  # e.g., 'business_id'

            # Debug logging
            logger.debug(f"BulkModelSerializer - Found FK field '{fk_name}' -> '{fk_attname}' in data keys: {list(internal_data.keys())}")

            # Check if this field is a SlugRelatedField - if so, skip conversion
            if fk_name in current_fields:
                serializer_field = current_fields[fk_name]
                if isinstance(serializer_field, serializers.SlugRelatedField):
                    logger.debug(f"BulkModelSerializer - Skipping conversion for SlugRelatedField '{fk_name}'")
                    continue

            # Convert standard field name to _id field if present
            if fk_name in internal_data and fk_attname not in internal_data:
                # Copy the value to *_id field but keep the original for validation
                internal_data[fk_attname] = internal_data[fk_name]
                logger.debug(f"BulkModelSerializer - Converted '{fk_name}': {internal_data[fk_attname]} -> '{fk_attname}' (kept original for validation)")

        logger.debug(f"BulkModelSerializer - Final internal_data: {internal_data}")
        
        # Debug: Check field required status for all FK fields right before validation
        for model_field in self.Meta.model._meta.get_fields():
            if isinstance(model_field, ForeignKey):
                fk_name = model_field.name
                if fk_name in current_fields:
                    field = current_fields[fk_name]
                    logger.debug(f"BulkModelSerializer - Field '{fk_name}' required at validation time: {getattr(field, 'required', 'NO_ATTR')}")
        
        return super().to_internal_value(internal_data)
