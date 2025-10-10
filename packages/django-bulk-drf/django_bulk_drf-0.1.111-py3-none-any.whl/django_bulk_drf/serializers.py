from django.db.models import ForeignKey
from rest_framework import serializers


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

    # Cache for FK field mappings to avoid repeated lookups
    _fk_field_cache = None

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
                    continue

            # Add the *_id field if it's not already defined
            if fk_attname not in fields:
                fields[fk_attname] = serializers.IntegerField(
                    required=False,  # Make it optional since we convert from the standard field
                    allow_null=model_field.null,
                    write_only=True,  # Only for input, not output
                )

            # Make the original FK field not required since we'll convert to *_id
            # But only if it's not a SlugRelatedField (those stay required as they are)
            if fk_name in fields:
                original_field = fields[fk_name]
                if not isinstance(original_field, serializers.SlugRelatedField):
                    # Simply modify the existing field's required attribute instead of recreating it
                    if hasattr(original_field, 'required'):
                        original_field.required = False

        return fields

    def _get_fk_field_mappings(self):
        """
        Build and cache FK field mappings to avoid repeated lookups.
        Returns dict mapping fk_name -> (fk_attname, is_slug_field)
        """
        if self._fk_field_cache is None:
            self._fk_field_cache = {}
            model = self.Meta.model
            current_fields = self.fields  # Use cached fields
            
            for model_field in model._meta.get_fields():
                if not isinstance(model_field, ForeignKey):
                    continue
                
                fk_name = model_field.name
                fk_attname = model_field.attname
                
                # Check if this is a SlugRelatedField
                is_slug_field = False
                if fk_name in current_fields:
                    serializer_field = current_fields[fk_name]
                    if isinstance(serializer_field, serializers.SlugRelatedField):
                        is_slug_field = True
                
                self._fk_field_cache[fk_name] = (fk_attname, is_slug_field)
        
        return self._fk_field_cache

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

        # Use cached FK field mappings
        fk_mappings = self._get_fk_field_mappings()
        
        # Process all foreign key fields using cached mappings
        for fk_name, (fk_attname, is_slug_field) in fk_mappings.items():
            # Skip slug fields
            if is_slug_field:
                continue
            
            # Convert standard field name to _id field if present
            if fk_name in internal_data and fk_attname not in internal_data:
                # Copy the value to *_id field but keep the original for validation
                internal_data[fk_attname] = internal_data[fk_name]
                # Remove the original FK field to avoid expensive FK validation
                # since we've already converted to *_id
                del internal_data[fk_name]
        
        return super().to_internal_value(internal_data)
