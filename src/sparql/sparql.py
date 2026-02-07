from rdflib import Graph
from rdflib.namespace import RDF
from src.utils import build_parameters

class SparQL:
    def __init__(self, ontology_path: str):
        self.g = Graph()
        self.g.parse(ontology_path)
        self.prefix = (
            "PREFIX foaf: <http://www.ime.usp.br/~renata/FOAF-modified>\n"
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n\n"
        )

    def query_by_actor(self, actor: str = ""):

        print("[INFO] Procurando por ator")

        sparql_query = self.prefix + (
            "SELECT DISTINCT ?Movies\n"
            "WHERE {\n"
            f'?dir rdfs:label "{actor}" .'
            '?dir foaf:acts ?mov .'
            '?mov rdfs:label ?Movies .'
            "}\n"
        )

        query_return = self.g.query(sparql_query)

        results = []
        for row in query_return:
            print(row)
            results.append({
                "movie_title": str(row.Movies) if getattr(row, 'Movies', None) is not None else None,
            })

        return results
    
    def query_by_movie(self, movie: str = ""):
        
        return
    
    def query_by_director(self, director: str = ""):
        return
    
    def query(self, actor: str = "", title: str = "", director: str = "") -> list[dict]:

        if actor:
            return self.query_by_actor(actor)
        
        if title:
            return self.query_by_movie(title)
        
        if director:
            return self.query_by_director(director)
        
        return []