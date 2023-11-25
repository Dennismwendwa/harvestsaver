from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class DimensionsValidator(RegexValidator):
    """Validation class for dimension field"""
    regex = r"^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$"
    message = f"Enter valid dimensions (e.g., 7x8x9)"

    def __init__(self, *args, **kwargs):
        super().__init__(regex=self.regex, message=self.message, *args, **kwargs)
    def __call__(self, value):
        self.validate(value)

    def validate(self, value):
        dimensions = value.split("x")
        if len(dimensions) != 3:
            raise ValidationError(self.message)

        try:
            float(dimensions[0])
            float(dimensions[1])
            float(dimensions[2])

        except ValueError:
            raise ValidationError(self.message)
