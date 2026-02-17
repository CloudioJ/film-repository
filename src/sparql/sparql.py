from rdflib import Graph
from services.tmdb import TMDb

class SparQL:
    def __init__(self, ontology_path: str):
        self.g = Graph()
        self.g.parse(ontology_path)
        self.tmdb = TMDb()
        self.prefix = (
            "PREFIX foaf: <http://www.ime.usp.br/~renata/FOAF-modified>\n"
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n\n"
        )

    def query_by_actor(self, actor: str = "") -> list[dict]:
        print(f"[INFO] Procurando por ator: {actor}")

        sparql_query = self.prefix + (
            "SELECT DISTINCT ?Movies ?launchDate\n"
            "WHERE {\n"
            f'  ?actor rdfs:label "{actor}" .\n'
            "  ?actor foaf:acts ?mov .\n"
            "  ?mov rdfs:label ?Movies .\n"
            "  ?mov foaf:launchDate ?launchDate .\n"
            "}\n"
            "GROUP BY ?Movies ?launchDate"
        )
        query_return = self.g.query(sparql_query)
        results = []
        
        for row in query_return:
            movie_title = getattr(row, 'Movies', None)
            launch_date = getattr(row, 'launchDate', None)

            poster_path = self.tmdb.get_poster(movie_title, launch_date)
            results.append({
                "movie_title": str(movie_title) if movie_title else None,
                "launch_date": str(launch_date) if launch_date else None,
                "poster": poster_path
            })

        return results

    def query_by_movie(self, movie: str = "") -> dict:
        print(f"[INFO] Procurando por filme: {movie}")

        sparql_query = self.prefix + (
            "SELECT DISTINCT ?Movies "
            "(GROUP_CONCAT(DISTINCT ?actor; separator=', ') AS ?actors) "
            "(GROUP_CONCAT(DISTINCT ?director; separator=', ') AS ?directors)\n"
            "WHERE {\n"
            "  ?mov rdfs:label ?movieName .\n"
            f"  FILTER(CONTAINS(LCASE(STR(?movieName)), LCASE('{movie}')))\n"
            "  OPTIONAL { ?act foaf:acts ?mov . ?act rdfs:label ?actor . }\n"
            "  OPTIONAL { ?dir foaf:made ?mov . ?dir rdfs:label ?director . }\n"
            "  BIND(?movieName AS ?Movies)\n"
            "}\n"
            "GROUP BY ?Movies\n"
        )

        query_return = self.g.query(sparql_query)

        poster_path = self.tmdb.get_poster(movie)

        results = []

        for row in query_return:
            actors_str = str(row.actors) if getattr(row, 'actors', None) else ""
            actors_list = [a.strip() for a in actors_str.split(',')] if actors_str else []

            directors_str = str(row.directors) if getattr(row, 'directors', None) else ""
            directors_list = [a.strip() for a in directors_str.split(',')] if directors_str else []

            results.append({
                "movie": str(row.Movies),
                "poster": poster_path,
                "actors": actors_list,
                "director": directors_list
            })

        return results

    def query_by_director(self, director: str = "") -> list[dict]:
        print(f"[INFO] Procurando por filmes do diretor: {director}")

        sparql_query = self.prefix + (
            "SELECT DISTINCT ?Movies "
            "(GROUP_CONCAT(DISTINCT ?actor; separator=', ') AS ?actors)\n"
            "WHERE {\n"
            "  ?dir rdfs:label ?dirName .\n"
            f"  FILTER(CONTAINS(LCASE(STR(?dirName)), LCASE('{director}')))\n"
            "  ?dir foaf:made ?mov .\n"
            "  ?mov rdfs:label ?Movies .\n"
            "  OPTIONAL { ?act foaf:acts ?mov . ?act rdfs:label ?actor . }\n"
            "}\n"
            "GROUP BY ?Movies\n"
        )

        query_return = self.g.query(sparql_query)
        results = []

        for row in query_return:
            actors_str = str(row.actors) if getattr(row, 'actors', None) else ""
            actors_list = [a.strip() for a in actors_str.split(',')] if actors_str else []

            results.append({
                "movie": str(row.Movies),
                "actors": actors_list
            })

        return results
