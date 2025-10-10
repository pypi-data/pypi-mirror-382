"""Italy-specific PII recognizers."""
from presidio_analyzer.predefined_recognizers import (
    ItDriverLicenseRecognizer,
    ItFiscalCodeRecognizer,
    ItVatCodeRecognizer,
    ItIdentityCardRecognizer,
    ItPassportRecognizer,
)

COUNTRY_CODE = "IT"

RECOGNIZERS = [
    ItDriverLicenseRecognizer,
    ItFiscalCodeRecognizer,
    ItVatCodeRecognizer,
    ItIdentityCardRecognizer,
    ItPassportRecognizer,
]

ENTITY_TYPES = [
    "IT_DRIVER_LICENSE",
    "IT_FISCAL_CODE",
    "IT_VAT_CODE",
    "IT_IDENTITY_CARD",
    "IT_PASSPORT",
]


