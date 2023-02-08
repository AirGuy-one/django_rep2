from django.core.exceptions import ValidationError


def validate_quantity(value):
    if value <= 0:
        raise ValidationError(
            f'{value} is non-positive number',
            params={'value': value},
        )
