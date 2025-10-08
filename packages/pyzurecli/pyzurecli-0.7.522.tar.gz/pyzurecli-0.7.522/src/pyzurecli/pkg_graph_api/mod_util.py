def validate_range(min_val, max_val):
    def validator(value):
        if not (min_val <= value <= max_val):
            raise ValueError(f"Value must be between {min_val} and {max_val}, got {value}")
        return value
    return validator