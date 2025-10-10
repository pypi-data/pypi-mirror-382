"""USA-specific PII recognizers."""
from presidio_analyzer.predefined_recognizers import (
    UsSsnRecognizer,
    UsPassportRecognizer,
    UsLicenseRecognizer,
    UsItinRecognizer,
    UsBankRecognizer,
)

COUNTRY_CODE = "US"

RECOGNIZERS = [
    UsSsnRecognizer,
    UsPassportRecognizer,
    UsLicenseRecognizer,
    UsItinRecognizer,
    UsBankRecognizer,
]

ENTITY_TYPES = [
    "US_SSN",
    "US_PASSPORT",
    "US_DRIVER_LICENSE",
    "US_ITIN",
    "US_BANK_NUMBER",
]


