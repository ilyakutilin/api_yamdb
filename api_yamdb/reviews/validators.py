from datetime import datetime
from django.core.exceptions import ValidationError


def year_validator(value):
    if value > datetime.now().year:
        raise ValidationError(
            ('Год произведения не может быть больше текущего'),
            params={'value': value},
        )
