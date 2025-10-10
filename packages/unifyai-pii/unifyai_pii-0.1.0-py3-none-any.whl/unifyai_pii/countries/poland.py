"""Poland-specific PII recognizers."""
from presidio_analyzer.predefined_recognizers import (
    PlPeselRecognizer,
)

COUNTRY_CODE = "PL"

RECOGNIZERS = [
    PlPeselRecognizer,
]

ENTITY_TYPES = [
    "PL_PESEL",
]


