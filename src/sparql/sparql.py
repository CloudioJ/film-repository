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
            "SELECT DISTINCT ?Movies ?launchDate (GROUP_CONCAT(DISTINCT ?director; separator=', ') AS ?directors)\n"
            "WHERE {\n"
            f'?actor rdfs:label "{actor}" .\n'
            '?actor foaf:acts ?mov .\n'
            '?mov rdfs:label ?Movies .\n'
            '?mov foaf:launchDate ?launchDate .\n'
            'OPTIONAL { ?dir foaf:made ?mov . ?dir rdfs:label ?director . }\n'
            "}\n"
            "GROUP BY ?Movies ?launchDate\n"  # Add this line!
        )

        query_return = self.g.query(sparql_query)
        results = []

        for row in query_return:
            print(row)
            directors_str = str(row.directors) if getattr(row, 'directors', None) is not None else ""
            directors_list = [a.strip() for a in directors_str.split(',')] if directors_str else []
            results.append({
                "movie_title": str(row.Movies) if getattr(row, 'Movies', None) is not None else None,
                "launch_date": str(row.launchDate) if getattr(row, 'launchDate', None) is not None else None,
                "director": directors_list
            })
            
        return results
    
    def query_by_movie(self, movie: str = ""):
        
        print("[INFO] Procurando por filme")
        sparql_query = self.prefix + (
            "SELECT DISTINCT ?Movies (GROUP_CONCAT(DISTINCT ?actor; separator=', ') AS ?actors) (GROUP_CONCAT(DISTINCT ?director; separator=', ') AS ?directors)\n"
            "WHERE {\n"
            f'?mov rdfs:label "{movie}" .\n'
            '?mov rdfs:label ?Movies .\n'
            'OPTIONAL { ?act foaf:acts ?mov . ?act rdfs:label ?actor . }\n'
            'OPTIONAL { ?dir foaf:made ?mov . ?dir rdfs:label ?director . }\n'
            "}\n"
            "GROUP BY ?Movies\n"
        )
        query_return = self.g.query(sparql_query)
        
        results = []
        for row in query_return:
            print(row)
            
            actors_str = str(row.actors) if getattr(row, 'actors', None) is not None else ""
            actors_list = [a.strip() for a in actors_str.split(',')] if actors_str else []
            
            directors_str = str(row.directors) if getattr(row, 'directors', None) is not None else ""
            directors_list = [a.strip() for a in directors_str.split(',')] if directors_str else []

            results.append({
                "movie": str(row.Movies) if getattr(row, 'Movies', None) is not None else None,
                "actors": actors_list,
                "director": directors_list
            })

        return results
    
    def query_by_director(self, director: str = ""):
        return