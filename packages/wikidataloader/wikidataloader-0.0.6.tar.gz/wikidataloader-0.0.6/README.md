# wikidataloader

Easy pythonic wrapper around the [Wikidata SPARQL API](https://query.wikidata.org/) for quick creation of datasets from Wikidata.

Only supports simple, non-recursive queries - for complex queries please directly use the [SPARQL API](https://query.wikidata.org/) provided by Wikidata.

It does not support complex operators (ordering, datetime conversion, string/numeric filtering etc.), because these can be substituted by preprocessing the dataset in Python after retrieval.

## Usage

Look up the URIs for properties (e.g. _P31_) and objects (e.g. _Q5_) on [Wikidata's search engine](https://www.wikidata.org/).

```python
from wikidataloader import WikidataQuery

# Linguists from Germany with birth places and gender

results = WikidataQuery.search(
    # {is_instance:human, country_of_origin:Germany, profession:linguist}
    filters={"P31": "Q5", "P27": "Q183", "P106": "Q14467526"}, 

    # selects the properties "Gender" and "Birth Place" as columns in the dataframe and names them "Gender" and "City of Birth"
    select=[("P21", "Gender"), ("P19", "City of Birth")],

    # returns a maximum of 5 results
    limit=5,

    # retrieves labels in English, if available
    default_language="en" 
).to_pandas()

results

>>>                                    item Gender        City_of_Birth
>>> 0                        Hermann Weller   male     Schwäbisch Gmünd
>>> 1                             Hans Wehr   male              Leipzig
>>> 2                       Theodor Haecker   male            Mulfingen
>>> 3                   Gottfried Bernhardy   male  Gorzów Wielkopolski
>>> 4                    Wilhelm Streitberg   male   Rüdesheim am Rhein

```

For more examples, see [example.ipynb](./example.ipynb)

## Install

Install using pip:

```pip install wikidataloader```

## Limitations

- Does not support recursive queries
- Does not support Senses and Forms for Lexeme queries 
