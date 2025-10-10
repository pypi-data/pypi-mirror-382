"""Country-specific PII recognizer modules for Presidio."""

# List of country modules
__all__ = [
    "india",
    "usa",
    "uk",
    "spain",
    "italy",
    "australia",
    "singapore",
    "poland",
    "finland",
]

# Optional: convenience imports for direct access (not required for dynamic loader)
from . import india
from . import usa
from . import uk
from . import spain
from . import italy
from . import australia
from . import singapore
from . import poland
from . import finland
