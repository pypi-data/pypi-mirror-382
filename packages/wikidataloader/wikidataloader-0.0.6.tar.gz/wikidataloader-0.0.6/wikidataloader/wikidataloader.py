"""
This module provides an easy pythonic wrapper around the Wikidata SPARQL API (https://query.wikidata.org/) for quick creation of simple datasets from Wikidata.
"""

import warnings
import re
import requests
import pandas as pd

class WikidataQuery:
    """
    Sends a SPARQL query to the Wikidata API and stores the result as a pandas DataFrame.

    Instantiate with the class methods WikidataQuery.search() or WikidataQuery.from_sparql_query().
    """
    REGEX_PROPERTY = re.compile(r"P\d+")
    REGEX_ITEM = re.compile(r"Q\d+")

    def __init__(self, query: str, _df: pd.DataFrame):
        self.query: str = query
        self._df: pd.DataFrame = _df

    @classmethod
    def search(cls, filters: dict[str, str], select: list[str, str] | None = None, negative_filters: dict[str, str] | None = None, required_properties: set[str] | None = None, retrieve_lexicographical_information: bool = False, default_language: str = "[AUTO_LANGUAGE]", limit: int | None = None):
        """
        Creates a SPARQL query and creates a WikidataQuery object based on the response from Wikidata.

        :param filters: Dictionary of properties and the corresponding values that the selected items should have. For example {"P31": "Q3624078", "P30": "Q15"}. Please use the URIs from Wikidata.
        :param select: List of tuples of properties that should be returned as columns in the DataFrame. The first element of the tuple should be the URI from Wikidata, the second element should be a name for the column. For example: [("P36", "Capital"), ("P37", "Languages"), ("P625", "Coordinates")]. The title/name of the item itself will always be part of the filters and should not be explicitly added here. Default is None, which does not select any other features than the item description.
        :param negative_filters: Dictionary of properties and the corresponding values that the selected items should not have. For example {"P31": "Q3624078", "P30": "Q15"}. Please use the URIs from Wikidata. Default is None, which does not exclude any elements.
        :param required_properties: Set of properties retrieved by 'select' that cannot be None. Default is None, which means no property is required.
        :param retrieve_lexicographical_information: If True, retrieves the lexicographical properties "lemma", "language" and "lexical_category". Only use this, if you expect your data to be Lexemes instead of Items. Default is False.
        :param default_language: Default language for the label service. Default is "[AUTO_LANGUAGE]", which defaults to the language of your operating system.
        :param limit: Maximum number of results. If None, this will return all results. Default is None.

        :returns: new WikidataQuery object
        :raises ValueError: if filters is empty: Wikidata can't parse a query on all objects in the database.
        """
        if not filters:
            raise ValueError("No features provided for 'filters'.")

        sparql_query = []

        # SELECT
        select = select or []
        select_statement = "SELECT DISTINCT ?itemLabel "

        if retrieve_lexicographical_information:
            select_statement += "?lemma ?languageLabel ?lexical_categoryLabel "

        for _, select_column_name in select:
            select_statement += f"?{select_column_name.replace(' ', '_')}Label "
        sparql_query.append(select_statement)

        # WHERE
        where_statement = "WHERE{\n"

        for filter_property, filter_value in filters.items():
            if not re.match(cls.REGEX_PROPERTY, filter_property):
                warnings.warn(f"Property '{filter_property}' is not in Wikidata URI format (P\\d+).")
            if not re.match(cls.REGEX_ITEM, filter_value):
                warnings.warn(f"Item '{filter_value}' is not in Wikidata URI format (Q\\d+).")
            where_statement += f"?item wdt:{filter_property} wd:{filter_value} .\n"

        if negative_filters:
            for filter_property, filter_value in negative_filters.items():
                if not re.match(cls.REGEX_PROPERTY, filter_property):
                    warnings.warn(f"Property '{filter_property}' is not in Wikidata URI format (P\\d+).")
                if not re.match(cls.REGEX_ITEM, filter_value):
                    warnings.warn(f"Item '{filter_value}' is not in Wikidata URI format (Q\\d+).")
                where_statement += "FILTER NOT EXISTS{?item wdt:" + filter_property + " wd:" + filter_value + " .}\n"
        
        required_properties = required_properties or set()
        for select_property, select_column_name in select:
            if not re.match(cls.REGEX_PROPERTY, select_property):
                warnings.warn(f"Property '{select_property}' is not in Wikidata URI format (P\\d+).")
            
            if select_property in required_properties:
                where_statement += "?item wdt:" + select_property + " ?" + select_column_name.replace(' ', '_') + " .\n"
            else:
                where_statement += "OPTIONAL{?item wdt:" + select_property + " ?" + select_column_name.replace(' ', '_') + " .}\n"

        if retrieve_lexicographical_information:
            where_statement += """OPTIONAL{?item wikibase:lemma ?lemma} \nOPTIONAL{?item dct:language ?language} \nOPTIONAL{?item wikibase:lexicalCategory ?lexical_category}\n"""

        
        where_statement += 'SERVICE wikibase:label { bd:serviceParam wikibase:language "' + default_language + ',[AUTO_LANGUAGE],mul,fr,ar,be,bg,bn,ca,cs,da,de,el,en,es,et,fa,fi,he,hi,hu,hy,id,it,ja,jv,ko,nb,nl,eo,pa,pl,pt,ro,ru,sh,sk,sr,sv,sw,te,th,tr,uk,yue,vec,vi,zh". }\n'
        where_statement += "}\n"
        sparql_query.append(where_statement)

        # LIMIT
        if not limit is None:
            sparql_query.append(f"LIMIT {limit}")

        sparql_query_str = "\n".join(sparql_query)
        _df = cls._retrieve_from_wikidata(sparql_query_str)
        _df.columns = [col[:-5] if col.endswith("Label") else col for col in _df.columns] # remove artifact in column names left by wikibase label service

        return cls(query = sparql_query_str, _df = _df)

    @classmethod
    def from_sparql_query(cls, sparql_query: str):
        """
        Create a WikidataQuery from a predefined query, written in SPARQL.

        :param sparql_query: Pre-written SPARQL query string
        :returns: new WikidataQuery object
        """
        _df = cls._retrieve_from_wikidata(sparql_query)
        return cls(query = sparql_query, _df = _df)

    def to_pandas(self) -> pd.DataFrame:
        """
        Convert WikidataQuery to pandas DataFrame.

        :returns: result of the Wikidata query, as pandas DataFrame
        """
        return self._df

    def to_hf_dataset(self) -> "datasets.Dataset":
        """
        Convert WikidataQuery to huggingface dataset.

        :returns: result of the Wikidata query, as datasets.Dataset
        :raises ModuleNotFoundError: if datasets is not installed
        """
        try:
            from datasets import Dataset
            return Dataset.from_pandas(self._df)
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Could not convert: datasets not installed")

    def to_polars(self) -> "polars.DataFrame":
        """
        Convert WikidataQuery to polars DataFrame.

        :returns: result of the Wikidata query, as polars DataFrame
        :raises ModuleNotFoundError: if polars is not installed
        """
        try:
            import polars
            return polars.from_pandas(self._df)
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Could not convert: polars not installed")

    @staticmethod
    def _retrieve_from_wikidata(sparql_query: str) -> pd.DataFrame:
        """
        Calls the Wikidata SPARQL API to retrieve data and saves it as a pandas DataFrame.

        :param sparql_query: Query written in SPARQL
        :returns: result of the Wikidata query, as pandas DataFrame
        """
        headers = { 'Accept': 'application/sparql-results+json' }
        params = {'query': sparql_query}
        response = requests.get("https://query.wikidata.org/sparql", headers=headers, params=params).json()


        # parse nested json response to list of dicts
        column_names = response["head"]["vars"]

        data = []
        for row in response["results"]["bindings"]:
            row_item = {col: row.get(col, {}).get("value", None) for col in column_names}
            data.append(row_item)

        return pd.DataFrame(data)

    def __repr__(self):
        return self._df.__repr__() + "\n\n(Wikidata Results)"

