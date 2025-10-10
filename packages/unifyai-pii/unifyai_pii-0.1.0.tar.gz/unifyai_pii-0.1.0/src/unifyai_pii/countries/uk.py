"""UK-specific PII recognizers."""
from presidio_analyzer.predefined_recognizers import (
    NhsRecognizer,
    UkNinoRecognizer,
)

COUNTRY_CODE = "UK"

RECOGNIZERS = [
    NhsRecognizer,
    UkNinoRecognizer,
]

ENTITY_TYPES = [
    "UK_NHS",
    "UK_NINO",
]


