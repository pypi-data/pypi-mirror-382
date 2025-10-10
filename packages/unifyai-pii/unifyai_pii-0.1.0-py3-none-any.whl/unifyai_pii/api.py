"""Public API helpers matching tests and integrating with Presidio AnalyzerEngine."""

from __future__ import annotations

from typing import Iterable, List, Sequence

from .loader import load_all_countries, load_country
from .registry import (
    create_recognizers,
    get_entity_types,
    get_registered_countries,
)


_CODE_ALIAS = {
    "GB": "UK",
}

_CODE_TO_MODULE = {
    "IN": "india",
    "US": "usa",
    "UK": "uk",
    "ES": "spain",
    "IT": "italy",
    "AU": "australia",
    "SG": "singapore",
    "PL": "poland",
    "FI": "finland",
}


def _normalize_country_code(code: str) -> str:
    c = code.strip().upper()
    return _CODE_ALIAS.get(c, c)


def _ensure_loaded_for_codes(codes: Sequence[str]) -> None:
    for code in codes:
        normalized = _normalize_country_code(code)
        module_name = _CODE_TO_MODULE.get(normalized)
        if not module_name:
            raise ValueError(f"Country code '{code}' not supported")
        # Load and register this module
        load_country(module_name)


def load_country_recognizers(code: str) -> List[object]:
    """Instantiate recognizers for a single country code (case-insensitive).

    Raises ValueError if the country code is unsupported.
    """
    normalized = _normalize_country_code(code)
    _ensure_loaded_for_codes([normalized])
    return create_recognizers(normalized)


def get_supported_countries() -> List[str]:
    """Return all supported country codes as a sorted list."""
    load_all_countries()
    return get_registered_countries()


def get_country_entity_types(code: str) -> List[str]:
    """Return entity type names for a country code or raise ValueError."""
    normalized = _normalize_country_code(code)
    _ensure_loaded_for_codes([normalized])
    entities = get_entity_types(normalized)
    if not entities:
        raise ValueError(f"Country code '{code}' not supported")
    return entities


def create_analyzer_with_countries(
    codes: Sequence[str],
    include_default_recognizers: bool = True,
):
    """Create a Presidio AnalyzerEngine and add specified country recognizers."""
    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

    if include_default_recognizers:
        analyzer = AnalyzerEngine()
    else:
        # Start with an empty registry to avoid default recognizers
        empty_registry = RecognizerRegistry()
        analyzer = AnalyzerEngine(registry=empty_registry)
    add_country_recognizers_to_analyzer(analyzer, codes)
    return analyzer


def add_country_recognizers_to_analyzer(analyzer, codes: Sequence[str]) -> None:
    """Add recognizers for given country codes to an existing AnalyzerEngine."""
    _ensure_loaded_for_codes(codes)
    for code in codes:
        normalized = _normalize_country_code(code)
        for rec in create_recognizers(normalized):
            analyzer.registry.add_recognizer(rec)


