"""Finland-specific PII recognizers."""
from presidio_analyzer.predefined_recognizers import (
    FiPersonalIdentityCodeRecognizer,
)

COUNTRY_CODE = "FI"

RECOGNIZERS = [
    FiPersonalIdentityCodeRecognizer,
]

ENTITY_TYPES = [
    "FI_PERSONAL_IDENTITY_CODE",
]


