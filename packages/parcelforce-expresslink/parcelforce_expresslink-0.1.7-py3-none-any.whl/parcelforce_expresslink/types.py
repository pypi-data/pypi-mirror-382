from __future__ import annotations

import re
from enum import StrEnum, Enum
from typing import Annotated

from pydantic import ValidationError, AfterValidator, BeforeValidator, Field, StringConstraints


class ShipmentType(StrEnum):
    DELIVERY = 'DELIVERY'
    COLLECTION = 'COLLECTION'


class DropOffInd(StrEnum):
    PO = 'PO'
    DEPOT = 'DEPOT'


class DeliveryKindEnum(str, Enum):
    DELIVERY = 'DELIVERY'
    COLLECTION = 'COLLECTION'


class ExpressLinkError(Exception): ...


class ExpressLinkWarning(Exception): ...


class ExpressLinkNotification(Exception): ...


pc_excluded = {'C', 'I', 'K', 'M', 'O', 'V'}


def validate_uk_postcode(v: str):
    pattern = re.compile(r'([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})')
    if not re.match(pattern, v) and not set(v[-2:]).intersection(pc_excluded):
        raise ValidationError('Invalid UK postcode')
    return v


POSTCODE_PATTERN = r'([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})'
VALID_POSTCODE = Annotated[
    str,
    AfterValidator(validate_uk_postcode),
    BeforeValidator(lambda s: s.strip().upper()),
    Field(..., description='A valid UK postcode'),
]


def string_type(length: int):
    return Annotated[str, StringConstraints(max_length=length)]
