from maleo.schemas.resource import Resource, ResourceIdentifier
from maleo.types.string import SequenceOfStrings


RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="xray", name="X-Ray", slug="xray")],
    details=None,
)


VALID_MIME_TYPE: SequenceOfStrings = [
    "application/dcm",
    "application/dicom",
    "image/jpg",
    "image/png",
]
