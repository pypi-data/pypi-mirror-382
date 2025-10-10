"""Presidio country recognizers package.

Public API:
 - load_all_countries(): discover and register all country recognizers
 - load_country(country): load/register a single country's recognizers
 - get_registered_countries(): list registered country codes
 - create_recognizers(country_code): instantiate recognizers for a country
 - get_entity_types(country_code): list of entity type names for a country
"""

from .loader import load_all_countries, load_country
from .registry import (
    get_registered_countries,
    create_recognizers,
    get_entity_types,
)
from .api import (
    load_country_recognizers,
    get_supported_countries,
    get_country_entity_types,
    create_analyzer_with_countries,
    add_country_recognizers_to_analyzer,
)

__all__ = [
    "load_all_countries",
    "load_country",
    "get_registered_countries",
    "create_recognizers",
    "get_entity_types",
    # Test-facing API
    "load_country_recognizers",
    "get_supported_countries",
    "get_country_entity_types",
    "create_analyzer_with_countries",
    "add_country_recognizers_to_analyzer",
]


