import NSO1212v1 as nso

from importlib import reload

reload(nso)

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
