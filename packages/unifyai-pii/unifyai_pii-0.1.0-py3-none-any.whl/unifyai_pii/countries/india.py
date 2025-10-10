"""India-specific PII recognizers."""
from presidio_analyzer.predefined_recognizers import (
    InAadhaarRecognizer,
    InPanRecognizer,
    InPassportRecognizer,
    InVehicleRegistrationRecognizer,
    InVoterRecognizer,
)

COUNTRY_CODE = "IN"

RECOGNIZERS = [
    InAadhaarRecognizer,
    InPanRecognizer,
    InPassportRecognizer,
    InVehicleRegistrationRecognizer,
    InVoterRecognizer,
]

ENTITY_TYPES = [
    "IN_AADHAAR",
    "IN_PAN",
    "IN_PASSPORT",
    "IN_VEHICLE_REGISTRATION",
    "IN_VOTER",
]


