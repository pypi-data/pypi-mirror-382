# simpleiso3166

[![PyPI - Version](https://img.shields.io/pypi/v/simpleiso3166.svg)](https://pypi.org/project/simpleiso3166)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/simpleiso3166.svg)](https://pypi.org/project/simpleiso3166)
[![codecov](https://codecov.io/github/stumpylog/simpleiso3166/graph/badge.svg?token=vEIsys5kmZ)](https://codecov.io/github/stumpylog/simpleiso3166)

---

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [Features](#features)
  - [Why](#why)
- [Usage](#usage)
  - [Country Based Interface](#country-based-interface)
  - [Subdivision Based Interface](#subdivision-based-interface)
- [Roadmap](#roadmap)

## Installation

```console
pip install simpleiso3166
```

For the searching by partial name, include the extra:

```console
pip install simpleiso3166[search]
```

## License

`simpleiso3166` is distributed under the terms of the [MPL-2.0](https://spdx.org/licenses/MPL-2.0.html) license.

## Features

- Strongly typed interface to ISO 3166-1 countries and ISO 3166-2 subdivisions (e.g. states, provinces)
- No JSON parsing at runtime, fully & statically defined in Python
- Includes defined types to allow integration with libraries like Pydantic for validation of code validity
  - `from simpleiso3166 import CountryCodeAlpha2Type` for example, provides a Literal of all alpha-2 codes
- Searching for countries by exact or partial name
- Searching for subdivisions by exact or partial name
- Supports Python 3.9+
- On Python 3.10 and newer, uses `slots` to efficiently store country and subdivision data

### Why?

This library was created as a way to provide strongly typed access to the ISO 3166 standard, which is used to define country codes and subdivision codes.
It's designed to be lightweight and easy to use in Python projects.

Other existing libraries include [pycountry](https://github.com/pycountry/pycountry), but they don't provide the same
strongly typed interface as this library does. They also load JSON files at runtime, which can be a performance issue and takes
memory.

## Usage

### Country Based Interface

If you know the country's code:

```python
country = Country.from_alpha2("US")

assert country.official_name == "United States of America"
assert country.name == "United States"

# ISO-3166 includes things like districts and territories
assert len(country.subdivisions) == 57
```

If you need to search for the country:

```python
results = list(Country.from_partial_name("Kingdom"))

assert len(results) == 17
assert results[0].alpha2 == "BE"
assert results[0].name == "Kingdom of Belgium"
assert results[0].common_name == "Belgium"

assert results[10].alpha2 == "NL"
assert results[10].name == "Kingdom of the Netherlands"
assert results[10].common_name == "Netherlands"

assert results[16].alpha2 == "TO"
assert results[16].name == "Kingdom of Tonga"
assert results[16].common_name == "Tonga"
```

Access a particular subdivision:

```python
country = Country.from_alpha2("DE")

# You can check this subdivision code is in this country
assert country.contains_subdivision("DE-BW")

# This will return None if the subdivision isn't valid
subdivision = country.get_subdivision("DE-BW")
assert subdivision.name == "Baden-Württemberg"
```

### Subdivision Based Interface

Search for a subdivision by name:

```python
results = list(Subdivision.search_by_name("Connecticut"))

assert len(results) == 1
assert results[0] == "US-CT"
```

## Roadmap

### Improved Searching

This is partly implemented, but more would be helpful

- Search using common aliases for countries (e.g. "USA" for "United States of America")
- Extended searching for subdivisions by common aliases (eg "DC" for "Washington DC")
- Search using re-ordered names (e.g. "The Democratic Republic of the Congo" for instead of "Congo, The Democratic Republic of the")

### ISO 3166-3

- Access to deleted country data
