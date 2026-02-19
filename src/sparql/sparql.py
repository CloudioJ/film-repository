import time
import concurrent.futures
from rdflib import Graph
from services.tmdb import TMDb

class SparQL:
    def __init__(self, ontology_path: str):
        self.g = Graph()
        self.g.parse(ontology_path)
        self.tmdb = TMDb()
        self.prefix = (
            "PREFIX : <http://www.semanticweb.org/ontologies/2023/movies#>\n"
            "PREFIX foaf: <http://www.ime.usp.br/~renata/FOAF-modified>\n"
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n\n"
        )

    def query_by_actor(self, actor: str = "", direct: bool = False) -> dict:
        print(f"[INFO] Procurando por ator: {actor}")

        if direct:
            filter_clause = f'?actor rdfs:label ?actorName . FILTER(STR(?actorName) = "{actor}")\n'
        else:
            filter_clause = f'?actor rdfs:label ?actorName . FILTER(CONTAINS(LCASE(STR(?actorName)), LCASE("{actor}")))\n'

        sparql_query = self.prefix + (
            "SELECT DISTINCT ?actorName ?Movies ?launchDate\n"
            "WHERE {\n"
            f"{filter_clause}"
            "  ?actor foaf:acts ?mov .\n"
            "  ?mov rdfs:label ?Movies .\n"
            "  ?mov foaf:launchDate ?launchDate .\n"
            "}\n"
            "GROUP BY ?Movies ?launchDate ?actorName"
        )

        query_return = self.g.query(sparql_query)
        movies_data = []
        actor_name = None

        for row in query_return:
            if not actor_name:
                actor_name = getattr(row, 'actorName', None)
                print(f"[INFO] Retorno do nome do ator: {actor_name}")
            movie_title = getattr(row, 'Movies', None)
            movie_year = getattr(row, 'launchDate', None)
            if movie_title:
                movies_data.append((str(movie_title), str(movie_year) if movie_year else ""))

        person_image = self.tmdb.get_person_image(actor_name)

        def process_movie(data):
            title, year = data
            tmdb_data = self.tmdb.get_movie_data(title)
            return {
                "movie_title": title,
                "year": year,
                "poster": tmdb_data.get("poster"), 
                "rating": tmdb_data.get("rating"),
                "overview": tmdb_data.get("overview") 
            }

        with concurrent.futures.ThreadPoolExecutor() as executor:
            movie_list = list(executor.map(process_movie, movies_data))

        return {
            "person_image": person_image,
            "person_name": actor_name,
            "movies": movie_list
        }

    def query_by_movie(self, movie: str = "", direct: bool = False) -> list[dict]:
        print("[INFO] Procurando por filme")

        direct_query = (
            "SELECT DISTINCT ?Movies ?year (GROUP_CONCAT(DISTINCT ?actor; separator=', ') AS ?actors) (GROUP_CONCAT(DISTINCT ?director; separator=', ') AS ?directors)\n"
            "WHERE {\n"
            f'?mov rdfs:label "{movie}" .\n'
            '?mov rdfs:label ?Movies .\n'
            '?mov foaf:launchDate ?year .\n'
            'OPTIONAL { ?act foaf:acts ?mov . ?act rdfs:label ?actor . }\n'
            'OPTIONAL { ?dir foaf:made ?mov . ?dir rdfs:label ?director . }\n'
            "}\n"
            "GROUP BY ?Movies\n"
        )

        fuzzy_query = (
            "SELECT DISTINCT ?Movies ?year (GROUP_CONCAT(DISTINCT ?actor; separator=', ') AS ?actors) (GROUP_CONCAT(DISTINCT ?director; separator=', ') AS ?directors)\n"
            "WHERE {\n"
            '?mov rdfs:label ?Movies .\n'
            '?mov foaf:launchDate ?year .\n'
            f'FILTER(CONTAINS(LCASE(str(?Movies)), LCASE("{movie}")))\n'
            'OPTIONAL { ?act foaf:acts ?mov . ?act rdfs:label ?actor . }\n'
            'OPTIONAL { ?dir foaf:made ?mov . ?dir rdfs:label ?director . }\n'
            "}\n"
            "GROUP BY ?Movies\n"
        )

        sparql_query = self.prefix + direct_query if direct else self.prefix + fuzzy_query

        query_return = self.g.query(sparql_query)

        movies_list = []
        for row in query_return:
            actors_str = str(row.actors) if getattr(row, 'actors', None) is not None else ""
            actors_list = [a.strip() for a in actors_str.split(',')] if actors_str else []
            
            directors_str = str(row.directors) if getattr(row, 'directors', None) is not None else ""
            directors_list = [a.strip() for a in directors_str.split(',')] if directors_str else []

            movie_title = str(row.Movies) if getattr(row, 'Movies', None) is not None else None
            movie_year = str(row.year) if getattr(row, 'year', None) is not None else ""
            
            if movie_title:
                movies_list.append((movie_title, actors_list, directors_list, movie_year))

        def process_movie(data):
            title, actors, directors, year = data
            movie_info = self.tmdb.get_movie_data(title)
            return {
                "movie_title": title,
                "year": year,
                "actors": actors_list,
                "director": directors_list,
                "overview": movie_info.get("overview"),
                "poster": movie_info.get("poster"),
                "rating": movie_info.get("rating")
            }

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_movie, movies_list))
            
        return results

    def query_by_director(self, director: str = "", direct: bool = False) -> dict:
        print(f"[INFO] Procurando por filmes do diretor: {director}")

        if direct:
            filter_clause = f'?dir rdfs:label ?dirName . FILTER(STR(?dirName) = "{director}")\n'
        else:
            filter_clause = (
                "  ?dir rdfs:label ?dirName .\n"
                f"  FILTER(CONTAINS(LCASE(STR(?dirName)), LCASE('{director}')))\n"
            )

        sparql_query = self.prefix + (
            "SELECT DISTINCT ?dirName ?Movies ?year "
            "(GROUP_CONCAT(DISTINCT ?actor; separator=', ') AS ?actors)\n"
            "WHERE {\n"
            f"{filter_clause}"
            "  ?dir foaf:made ?mov .\n"
            "  ?mov rdfs:label ?Movies .\n"
            "  ?mov foaf:launchDate ?year .\n"
            "  OPTIONAL { ?act foaf:acts ?mov . ?act rdfs:label ?actor . }\n"
            "}\n"
            "GROUP BY ?Movies ?dirName ?year\n"
        )

        query_return = self.g.query(sparql_query)
        
        movies_data = []
        dir_name = None

        for row in query_return:
            if not dir_name:
                dir_name = getattr(row, 'dirName', None)
            actors_str = str(row.actors) if getattr(row, 'actors', None) else ""
            actors_list = [a.strip() for a in actors_str.split(',')] if actors_str else []
            movie_title = str(row.Movies)
            movie_year = str(row.year) if getattr(row, 'year', None) is not None else ""
            if movie_title:
                movies_data.append((movie_title, actors_list, movie_year))

        person_image = self.tmdb.get_person_image(dir_name)
        def process_movie(data):
            title, actors, year = data
            tmdb_data = self.tmdb.get_movie_data(title)
            return {
                "movie_title": title,
                "year": year,
                "poster": tmdb_data.get("poster"),
                "rating": tmdb_data.get("rating"),
                "overview": tmdb_data.get("overview"),
                "actors": actors
            }

        with concurrent.futures.ThreadPoolExecutor() as executor:
            movie_list = list(executor.map(process_movie, movies_data))

        return {
            "person_image": person_image,
            "person_name": dir_name,
            "movies": movie_list
        }