# NSO1212v1

*National Statistical Office of Mongolia's Open Data API v1 Handler for Python*

A lightweight Python client for accessing the [1212.mn National Statistics Office of Mongolia API](https://www.1212.mn/en/data-base/open-data).
This package simplifies data retrieval by converting API responses into clean, easy-to-analyze **pandas DataFrames**.

---

## Features

- Retrieve **sectors**, **subsectors**, **tables**, **table meta data**, and **data** from 1212.mn.
- Validate query parameters before sending API requests.
- Handle language selection (`mn` or `en`).
- Convert JSON responses into `pandas.DataFrame` objects for convenient analysis.
- Support for JSON formatted responses.

---

## Installation

```bash
pip install NSO1212v1
```

Or install directly from source:

```bash
git clone https://github.com/makhgal-ganbold/NSO1212v1
cd NSO1212v1
pip install .
```

## Dependencies

* pandas
* requests
* itertools (standard library)

Install dependencies with:

```bash
pip install pandas requests
```

## Quick Start

```python
import NSO1212v1 as nso

# Get list of all sectors

sectors = nso.sectors(language="en")
sector_id = sectors.id[5]

# Get subsectors of a sector

subsectors = nso.subsectors(sector_id, language="en")
subsector_id = subsectors.id[0]

# Get tables available under a subsector

tables = nso.tables(sector_id, subsector_id, language="en")
table_id = tables.id[5]

# Get metadata of a specific table

table = nso.table(sector_id, subsector_id, table_id, language="en")
table["variables"]

# Query actual data

query = {
  "query": [
    {
      "code": "Байршил",
      "selection": {
        "filter": "item",
        "values": ["0"]
      }
    },
    {
      "code": "Бүс",
      "selection": {
        "filter": "item",
        "values": ["0"]
      }
    },
    {
      "code": "Он",
      "selection": {
        "filter": "item",
        "values": ["0", "1"]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}
data = nso.data(sector_id, subsector_id, table_id, query=query, language="en")

# The API response contains both raw JSON and a DataFrame
data
data["df"]
```

## Author

[Makhgal Ganbold](https://www.galaa.net/), National University of Mongolia

## Copyright

&copy; 2025 Makhgal Ganbold