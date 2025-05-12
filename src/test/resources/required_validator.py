class RequiredValidator:
    def validate_required(self, field, params):
        value = params.get(field.field_property)
        return value is not None and str(value).strip() != ""