from typing import Callable, Dict
from uuid import UUID
from maleo.schemas.resource import Resource, ResourceIdentifier
from ..enums.record import IdentifierType
from ..types.record import IdentifierValueType


IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType,
    Callable[..., IdentifierValueType],
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
}


RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="records", name="Records", slug="records")],
    details=None,
)
