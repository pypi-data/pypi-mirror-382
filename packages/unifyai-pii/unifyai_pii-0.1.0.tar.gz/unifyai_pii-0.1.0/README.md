# UnifyAi PII

[![PyPI version](https://badge.fury.io/py/unifyai-pii.svg)](https://badge.fury.io/py/unifyai-pii)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Country-specific PII recognizers for Microsoft Presidio - Easy loading of Aadhaar, PAN, SSN, and other country-specific PII detectors.

## Features

- 🌍 Multi-country support: India, USA, UK, Spain, Italy, Australia, Singapore, Poland, Finland
- 🔌 Simple API: Load recognizers with `load_country_recognizers('IN')`
- 🚀 Built on Presidio: Leverages Microsoft Presidio's proven PII detection
- 📦 Zero configuration: Works out of the box with sensible defaults

## Installation

```bash
pip install unifyai-pii
```

```python
from presidio_country_recognizers import create_analyzer_with_countries

analyzer = create_analyzer_with_countries(['IN', 'US'])

results = analyzer.analyze(
    text="My Aadhaar is 234123412346 and SSN is 078-05-1120",
    language="en"
)

for result in results:
    print(f"Found {result.entity_type}: {result.score}")
```

Repository: https://github.com/Vivek5143/unifyai-pii
