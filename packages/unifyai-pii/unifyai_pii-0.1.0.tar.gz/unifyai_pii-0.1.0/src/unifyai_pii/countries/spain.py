"""Spain-specific PII recognizers."""
from presidio_analyzer.predefined_recognizers import (
    EsNifRecognizer,
    EsNieRecognizer,
)

COUNTRY_CODE = "ES"

RECOGNIZERS = [
    EsNifRecognizer,
    EsNieRecognizer,
]

ENTITY_TYPES = [
    "ES_NIF",
    "ES_NIE",
]


