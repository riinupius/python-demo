import sys
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON, CSV, TSV

endpoint_url = "https://query.wikidata.org/sparql"

query = """ # World hospitals
SELECT DISTINCT ?item ?geo ?itemLabel
WHERE {
  ?item wdt:P31/wdt:P279* wd:Q16917;
        wdt:P625 ?geo .

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
}
LIMIT 1000
"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

results = get_results(endpoint_url, query)

hospitals = pd.json_normalize(results['results']['bindings'])

hospitals[['lon', 'lat']] = hospitals['geo.value'].str.extract(r'Point\(([-\d\.]+) ([-\d\.]+)\)').astype(float)
hospitals = hospitals[['item.value', 'itemLabel.value', 'lat', 'lon']].rename(columns={'item.value': 'id', 'itemLabel.value': 'label'})

hospitals.to_csv('data/world-hospitals.csv')
