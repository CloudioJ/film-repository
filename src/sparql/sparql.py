from rdflib import Graph
from rdflib.namespace import RDF
from src.utils import build_parameters

class SparQL:
    def __init__(self, ontology_path: str):
        self.g = Graph()
        self.g.parse(ontology_path)

    def query(self, actor: str = "", title: str = "", year: str = "") -> list[dict]:
        parameters = build_parameters(actor, title, year)

        prefix = (
            "PREFIX foaf: <http://www.ime.usp.br/~renata/FOAF-modified>"
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n\n"
        )

        sparql_query = prefix + (
            "SELECT DISTINCT ?Movies\n"
            "WHERE {\n"
            f"  {parameters}\n"
            "}\n"
        )

        print(f"Query enviado:\n{sparql_query}")

        results = []
        for row in self.g.query(sparql_query):
            print(row)
            results.append({
                "movie_title": str(row.Movies) if getattr(row, 'Movies', None) is not None else None,
            })

        return results