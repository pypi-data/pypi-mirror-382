
# NSO1212v1.py

# It supports the API v1.

import requests as r
import pandas as pd
import itertools

__all__ = ['sectors', 'subsectors', 'tables', 'table', 'data']

def __get(folder = "", language = "mn"):
  """
  Retrieve data from the 1212.mn API v1 for a specific folder and language.

  This function sends a GET request to the 1212.mn API and returns the JSON 
  response. If the response status code is not 200, it raises an exception.

  Parameters
  ----------
  folder : str, optional
      The folder or endpoint in the API to access (default is "").
  language : str, optional
      Language of the data, either 'mn' for Mongolian or 'en' for English.
      Any other value defaults to 'mn' (default is "mn").

  Returns
  -------
  dict
      Parsed JSON response from the API.

  Raises
  ------
  Exception
      If the API response status code is not 200.

  Examples
  --------
  >>> data = __get(folder="Historical data", language="en")
  >>> type(data)
  <class 'dict'>
  """
  if (language not in ("mn", "en")):
    language = "mn"
  response = r.get(url=f"https://data.1212.mn/api/v1/{language}/NSO/{folder}")
  if (response.status_code != 200):
    raise Exception(f"The server response status code is {response.status_code}.")
  return response.json()

def __df(json):
  """
  Convert a JSON object or list of dictionaries into a pandas DataFrame.

  This function takes a JSON object (typically a list of dictionaries) and 
  converts it into a pandas DataFrame for easier data manipulation and analysis.

  Parameters
  ----------
  json : dict or list of dict
      The JSON data to convert. Usually obtained from an API response.

  Returns
  -------
  pandas.DataFrame
      A DataFrame containing the data from the input JSON.

  Examples
  --------
  >>> data = [{"year": "2024", "population": 3544835}, {"year": "2023", "population": 3504741}]
  >>> df = __df(data)
  >>> print(df)
      year  population
  0   2024     3544835
  1   2023     3504741
  """
  df = pd.DataFrame(json)
  return df

def sectors(language = "mn"):
  """
  Retrieve sector ids and names from the 1212.mn API v1 and return it as 
  a pandas DataFrame.

  This function fetches sector information from the 1212.mn API, converts the 
  JSON response into a pandas DataFrame, and returns it for easy analysis.

  Parameters
  ----------
  language : str, optional
      Language of the data, either 'mn' for Mongolian or 'en' for English.
      Any other value defaults to 'mn' (default is "mn").

  Returns
  -------
  pandas.DataFrame
      A DataFrame containing sector data from the API.

  Raises
  ------
  Exception
      If the API response status code is not 200.

  Examples
  --------
  >>> df = sectors(language="en")
  >>> df.head()
	  id	                 type	text
  0	Economy, environment l	  Economy, environment
  1	Education, health	   l	  Education, health
  ...
  """
  sectors = __get(language = language)
  sectors = __df(sectors)
  return sectors

def subsectors(sector_id, language = "mn"):
  """
  Retrieve subsector IDs and names for a specific sector from the 1212.mn API v1 
  and return it as a pandas DataFrame.

  This function first validates the given sector ID against available sectors. 
  If valid, it fetches the corresponding subsector information from the API, 
  converts the JSON response into a pandas DataFrame, and returns it.

  Parameters
  ----------
  sector_id : str
      The ID of the sector for which subsector data is requested.
  language : str, optional
      Language of the data, either 'mn' for Mongolian or 'en' for English.
      Any other value defaults to 'mn' (default is "mn").

  Returns
  -------
  pandas.DataFrame
      A DataFrame containing subsector IDs and names for the given sector.

  Raises
  ------
  Exception
      If the provided sector ID is not valid.
      If the API response status code is not 200.

  Examples
  --------
  >>> df = subsectors(sector_id="Population, household", language="en")
  >>> df.head()
	  id	                             type	text
  0	1_Population, household	         l	  1_Population, household
  1	2_Regular movement of population l	  2_Regular movement of population
  ...
  """
  _sectors = sectors()
  if (sector_id not in _sectors.id.values):
    raise Exception("The sector id is not valid.")
  subsectors = __get(folder = sector_id, language = language)
  subsectors = __df(subsectors)
  return subsectors

def tables(sector_id, subsector_id, language = "mn"):
  """
  Retrieve table ids, names, and update information for a specific subsector of 
  a sector from the 1212.mn API v1 and return it as a pandas DataFrame.

  This function validates that the given subsector ID belongs to the specified 
  sector. If valid, it fetches the corresponding tables' data from the API, 
  converts the JSON response into a pandas DataFrame, and returns it.

  Parameters
  ----------
  sector_id : str
      The ID of the sector.
  subsector_id : str
      The ID of the subsector belonging to the given sector.
  language : str, optional
      Language of the data, either 'mn' for Mongolian or 'en' for English.
      Any other value defaults to 'mn' (default is "mn").

  Returns
  -------
  pandas.DataFrame
      A DataFrame containing tables' ids, names, and update information for
      the given sector and subsector.

  Raises
  ------
  Exception
      If the subsector ID does not belong to the given sector.
      If the API response status code is not 200.

  Examples
  --------
  >>> df = tables(sector_id="Population, household", subsector_id="1_Population, household", language="en")
  >>> df.head()
  	id                   type	text                                              updated
  0 DT_NSO_0300_001V2.px t    RESIDENT POPULATION IN MONGOLIA, by sex, singl...	2025-09-16T17:08:44
  1 DT_NSO_0300_001V3.px t    POPULATION OF MONGOLIA, by sex, single year of...	2025-09-16T17:07:30
  ...
  """
  _subsectors = subsectors(sector_id)
  if (subsector_id not in _subsectors.id.values):
    raise Exception("The subsector mismatches the sector.")
  tables = __get(folder = f"{sector_id}/{subsector_id}", language = language)
  tables = __df(tables)
  return tables

def table(sector_id, subsector_id, table_id, language = "mn"):
  """
  Retrieve a specific table meta data from the 1212.mn API v1 and return it as
  a structured dictionary.

  This function validates that the given table ID belongs to the specified 
  subsector and sector. It then fetches the corresponding table meta data from 
  the API and processes its "variables" component into a more structured format. 
  Each variable’s values and valueTexts are combined into a pandas DataFrame 
  for easier analysis.

  Parameters
  ----------
  sector_id : int or str
      The ID of the sector.
  subsector_id : int or str
      The ID of the subsector belonging to the given sector.
  table_id : int or str
      The ID of the table within the given subsector.
  language : str, optional
      Language of the data, either 'mn' for Mongolian or 'en' for English.
      Any other value defaults to 'mn' (default is "mn").

  Returns
  -------
  dict
      A dictionary representing the table data, where each variable contains:
      - `codes`: pandas.DataFrame with columns `values` and `valueTexts`
      - Other metadata fields from the API.

  Raises
  ------
  Exception
      If the table ID does not belong to the given subsector.
      If the API response status code is not 200.

  Examples
  --------
  >>> tbl = table(sector_id="Population, household", subsector_id="1_Population, household", table_id="DT_NSO_0300_004V1.px", language="en")
  >>> tbl["variables"][0]["codes"].head()
    values valueTexts
  0      0      Total
  1      1      Urban
  2      2      Rural
  """
  _tables = tables(sector_id, subsector_id)
  if (table_id not in _tables.id.values):
    raise Exception("The table id mismatches to the subsector.")
  table = __get(folder = f"{sector_id}/{subsector_id}/{table_id}", language = language)
  for i in range(len(table["variables"])):
    table["variables"][i]["codes"] = pd.DataFrame({"values":table["variables"][i]["values"],"valueTexts":table["variables"][i]["valueTexts"]})
    del table["variables"][i]["values"]
    del table["variables"][i]["valueTexts"]
  return table

def data(sector_id, subsector_id, table_id, query, language = "mn"):
  """
  Retrieve statistical data from the 1212.mn API v1, returning both raw JSON and 
  a pandas DataFrame representation.

  This function performs a filtered data request to the 1212.mn API for a specific 
  table. It first validates the query structure and the filter against the 
  available variables in the table, ensuring that filters are valid. 
  Once validated, it sends a POST request to the API and converts 
  the returned JSON response into a pandas DataFrame for convenient analysis.

  Parameters
  ----------
  sector_id : str
      The ID of the sector containing the desired table.
  subsector_id : str
      The ID of the subsector belonging to the given sector.
  table_id : str
      The ID of the table within the given subsector.
  query : dict
      A JSON-style query object used to request specific subsets of data. 
      Must include a `"response"` field equal to `{"format": "json-stat2"}` and 
      a `"query"` field defining variable selections, for example:

      ```
      {
          "query": [
              {
                  "code": "CODENAME",
                  "selection": {"filter": "item", "values": ["CODE0", "CODE1"]}
              }
          ],
          "response": {"format": "json-stat2"}
      }
      ```
  language : str, optional
      Language of the data, either `'mn'` for Mongolian or `'en'` for English.  
      Any other value defaults to `'mn'` (default is `"mn"`).

  Returns
  -------
  dict
      A dictionary representing the JSON API response, with an additional 
      key `"df"` containing a pandas DataFrame where:
      - Columns correspond to variable names.
      - Each row represents a combination of variable values.
      - The final column contains the observed values (labeled `"Хувьсагч"` 
        in Mongolian or `"Variable"` in English).

  Raises
  ------
  Exception
      If the query structure is invalid.
      If a code in the query is missing a `"filter"` entry.
      If query code values do not exist in the table metadata.
      If the API response status code is not 200.

  Examples
  --------
  >>> query = {
  ...     "query": [
  ...         {"code": "Байршил", "selection": {"filter": "item", "values": ["0"]}},
  ...         {"code": "Бүс", "selection": {"filter": "item", "values": ["0"]}},
  ...         {"code": "Он", "selection": {"filter": "item", "values": ["0", "1"]}}
  ...     ],
  ...     "response": {"format": "json-stat2"}
  ... }
  >>> data_nso = data("Population, household", "1_Population, household", "DT_NSO_0300_004V1.px", query, language="en")
  >>> data_nso["df"].head()
  	Location Region Year Variable
  0	Total    Total  2024 3544835
  1	Total    Total  2023 3504741
  2	Total    Total  2022 3457548
  """
  try:
    if (query["response"] != {"format": "json-stat2"}):
      raise Exception('The response parameter is not equal to {"format": "json-stat2"}.')
    _table = table(sector_id, subsector_id, table_id)
    __table = dict()
    for variable in _table["variables"]:
      __table[variable["code"]] = list(variable["codes"]["values"])
    del _table
    for code in query["query"]:
      if "filter" not in code["selection"]:
        raise Exception(f"The \"{code["code"]}\" code in the query parameter doesn't have the \"filter\" entry.")
      if not set(code["selection"]["values"]).issubset(set(__table[code["code"]])):
        raise Exception(f"The \"{code["code"]}\" code in the query parameter contains non-existing value.")
  except Exception:
    print("The query parameter is invalid ...")
    raise
  if (language not in ("mn", "en")):
    language = "mn"
  response = r.post(url=f"https://data.1212.mn:443/api/v1/{language}/NSO/{sector_id}/{subsector_id}/{table_id}", json=query)
  if (response.status_code != 200):
    raise Exception(f"The server response status code is {response.status_code}.")
  data = response.json()
  categories = dict()
  for id in data["id"]:
    categories[data["dimension"][id]["label"]] = list(data["dimension"][id]["category"]["label"].values())
  keys = list(categories.keys())
  values = list(categories.values())
  combinations = list(itertools.product(*values))
  df = pd.DataFrame(combinations, columns=keys)
  df["Хувьсагч" if language=="mn" else "Variable"] = data["value"]
  data["df"] = df
  return data
