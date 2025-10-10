"""Australia-specific PII recognizers."""
from presidio_analyzer.predefined_recognizers import (
    AuAbnRecognizer,
    AuAcnRecognizer,
    AuTfnRecognizer,
    AuMedicareRecognizer,
)

COUNTRY_CODE = "AU"

RECOGNIZERS = [
    AuAbnRecognizer,
    AuAcnRecognizer,
    AuTfnRecognizer,
    AuMedicareRecognizer,
]

ENTITY_TYPES = [
    "AU_ABN",
    "AU_ACN",
    "AU_TFN",
    "AU_MEDICARE",
]


