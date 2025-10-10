"""Dynamic loader for country-specific Presidio recognizers.

Scans the `presidio_country_recognizers.countries` package for modules and
registers each country's recognizer classes and entity types without hardcoding.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Any, Iterable, List, Optional

from . import countries as countries_pkg
from .registry import register_from_module


def discover_country_modules() -> List[str]:
    """Discover module names under the `countries` package.

    Returns module short names (e.g., "usa", "india").
    """
    module_names: List[str] = []
    for module_info in pkgutil.iter_modules(countries_pkg.__path__):
        if module_info.ispkg:
            # No nested packages expected at the moment
            continue
        module_names.append(module_info.name)
    return sorted(module_names)


def _infer_country_code_from_module_name(module_name: str) -> str:
    # Use simple mapping: usa -> US, uk -> UK, india -> IN, etc.
    # Prefer explicit COUNTRY_CODE if provided by module; this is only a fallback.
    name = module_name.strip().lower()
    special = {
        "usa": "US",
        "uk": "UK",
        "uae": "AE",
    }
    if name in special:
        return special[name]
    # Use first two characters if plausible, else first two letters of the name.
    if len(name) >= 2:
        return name[:2].upper()
    return name.upper()


def load_all_countries() -> List[str]:
    """Import and register all country modules.

    Returns the list of registered country codes.
    """
    registered: List[str] = []
    base_package = countries_pkg.__name__
    for mod_name in discover_country_modules():
        fqmn = f"{base_package}.{mod_name}"
        module = importlib.import_module(fqmn)
        country_code = getattr(module, "COUNTRY_CODE", None) or _infer_country_code_from_module_name(mod_name)
        register_from_module(country_code, module)
        registered.append(country_code)
    return sorted(set(registered))


def load_country(country: str) -> str:
    """Import and register a single country module if present.

    Returns the registered country code.
    """
    base_package = countries_pkg.__name__
    mod_name = country.strip().lower()
    fqmn = f"{base_package}.{mod_name}"
    module = importlib.import_module(fqmn)
    country_code = getattr(module, "COUNTRY_CODE", None) or _infer_country_code_from_module_name(mod_name)
    register_from_module(country_code, module)
    return country_code


