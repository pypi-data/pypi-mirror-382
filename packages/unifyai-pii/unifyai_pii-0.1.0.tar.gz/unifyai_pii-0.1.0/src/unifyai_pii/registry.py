"""Registry utilities for country-specific Presidio recognizers.

This module provides a simple in-memory registry that records, per country,
the recognizer classes and entity type constants exposed by that country's
module inside `presidio_country_recognizers.countries`.

Country modules are expected to define at least:
 - RECOGNIZERS: list[type] of Presidio Analyzer recognizer classes (not instances)
 - ENTITY_TYPES: list[str] of entity type names supported by those recognizers

Optionally, a module may define:
 - COUNTRY_CODE: explicit ISO-like country code (e.g., "US", "IN").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple, Type


RecognizerClass = Any  # Avoid importing presidio directly; accept any class type


@dataclass(frozen=True)
class CountryRecognizers:
    """Container for a country's recognizer metadata.

    Attributes
    ----------
    country_code: str
        Uppercase country code key (e.g., "US", "IN").
    recognizer_classes: list[type]
        List of recognizer classes (not instances) exported by the module.
    entity_types: list[str]
        List of entity type names handled by the recognizers.
    """

    country_code: str
    recognizer_classes: List[RecognizerClass]
    entity_types: List[str]


class _Registry:
    """Internal registry mapping country codes to recognizers and entities."""

    def __init__(self) -> None:
        self._by_country: MutableMapping[str, CountryRecognizers] = {}

    def register(self, country: str, recognizer_classes: Sequence[RecognizerClass], entity_types: Sequence[str]) -> CountryRecognizers:
        country_code = country.upper()
        record = CountryRecognizers(
            country_code=country_code,
            recognizer_classes=list(recognizer_classes),
            entity_types=list(entity_types),
        )
        self._by_country[country_code] = record
        return record

    def get(self, country: str) -> Optional[CountryRecognizers]:
        return self._by_country.get(country.upper())

    def countries(self) -> List[str]:
        return sorted(self._by_country.keys())

    def clear(self) -> None:
        self._by_country.clear()


_REGISTRY = _Registry()


def register_from_module(country_code: str, module: Any) -> CountryRecognizers:
    """Register recognizers for a country from a loaded module.

    The module must define `RECOGNIZERS` (list of classes) and `ENTITY_TYPES` (list of str).
    """
    recognizers = getattr(module, "RECOGNIZERS", None)
    entities = getattr(module, "ENTITY_TYPES", None)
    if not isinstance(recognizers, (list, tuple)) or not recognizers:
        raise ValueError(f"Module for {country_code} must define non-empty RECOGNIZERS list")
    if not isinstance(entities, (list, tuple)) or not entities:
        raise ValueError(f"Module for {country_code} must define non-empty ENTITY_TYPES list")
    return _REGISTRY.register(country_code, recognizers, entities)


def get_registered_countries() -> List[str]:
    """Return a sorted list of country codes registered so far."""
    return _REGISTRY.countries()


def get_recognizer_classes(country_code: str) -> List[RecognizerClass]:
    """Return recognizer classes registered for the given country, or empty list."""
    record = _REGISTRY.get(country_code)
    return list(record.recognizer_classes) if record else []


def get_entity_types(country_code: str) -> List[str]:
    """Return entity type names registered for the given country, or empty list."""
    record = _REGISTRY.get(country_code)
    return list(record.entity_types) if record else []


def create_recognizers(country_code: str, **kwargs: Any) -> List[Any]:
    """Instantiate recognizers for a country.

    Parameters
    ----------
    country_code: str
        Country code key used during registration.
    **kwargs: Any
        Optional kwargs to pass to each recognizer class constructor.
    """
    instances: List[Any] = []
    for cls in get_recognizer_classes(country_code):
        try:
            instances.append(cls(**kwargs))
        except TypeError:
            # Some recognizers may not accept kwargs; fall back to no-args constructor
            instances.append(cls())
    return instances


def _clear_registry_for_tests() -> None:
    """Clear registry (intended for tests)."""
    _REGISTRY.clear()


