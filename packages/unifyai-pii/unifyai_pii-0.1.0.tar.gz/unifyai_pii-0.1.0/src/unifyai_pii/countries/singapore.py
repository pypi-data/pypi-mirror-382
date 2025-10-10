"""Singapore-specific PII recognizers."""
from presidio_analyzer.predefined_recognizers import (
    SgFinRecognizer,
    SgUenRecognizer,
)

COUNTRY_CODE = "SG"

RECOGNIZERS = [
    SgFinRecognizer,
    SgUenRecognizer,
]

ENTITY_TYPES = [
    "SG_NRIC_FIN",
    "SG_UEN",
]


