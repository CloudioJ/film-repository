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

    def query_by_actor(self, actor: str = "") -> dict:
        print(f"[INFO] Procurando por ator: {actor}")

        # 1. Pega a foto do ator
        person_image = self.tmdb.get_person_image(actor)

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
        movie_list = []
        
        for row in query_return:
            movie_title = getattr(row, 'Movies', None)
            
            # Busca dados completos do filme (Poster, Nota, Sinopse)
            tmdb_data = self.tmdb.get_movie_data(str(movie_title))
            
            movie_list.append({
                "movie_title": str(movie_title) if movie_title else None,
                "poster": tmdb_data.get("poster"),   # Pega do novo dict
                "rating": tmdb_data.get("rating"),   # Pega a nota
                "overview": tmdb_data.get("overview") # Pega a sinopse
            })

        return {
            "person_image": person_image,
            "movies": movie_list
        }

    def query_by_movie(self, movie: str = "") -> list[dict]:
        print(f"[INFO] Procurando por filme: {movie}")

        # VOLTEI PARA A QUERY MAIS SIMPLES (Sem ?mov a :Movie)
        sparql_query = self.prefix + (
            "SELECT DISTINCT ?movieName ?actor ?director\n"
            "WHERE {\n"
            "  ?mov rdfs:label ?movieName .\n"
            f"  FILTER(CONTAINS(LCASE(STR(?movieName)), LCASE('{movie}')))\n"
            "  OPTIONAL { ?act foaf:acts ?mov . ?act rdfs:label ?actor . }\n"
            "  OPTIONAL { ?dir foaf:made ?mov . ?dir rdfs:label ?director . }\n"
            "}\n"
        )

        try:
            query_return = self.g.query(sparql_query)
        except Exception as e:
            print(f"[ERRO] Falha na consulta SPARQL: {e}")
            return []

        movies_map = {}

        for row in query_return:
            title = str(row.movieName)

            if title not in movies_map:
                # Busca dados no TMDB
                tmdb_data = self.tmdb.get_movie_data(title)
                
                movies_map[title] = {
                    "movie_title": title,
                    "poster": tmdb_data.get("poster"),
                    "overview": tmdb_data.get("overview"),
                    "rating": tmdb_data.get("rating"),
                    "actors": [],
                    "director": []
                }

            if getattr(row, 'actor', None):
                actor_name = str(row.actor)
                if actor_name not in movies_map[title]["actors"]:
                    movies_map[title]["actors"].append(actor_name)

            if getattr(row, 'director', None):
                director_name = str(row.director)
                if director_name not in movies_map[title]["director"]:
                    movies_map[title]["director"].append(director_name)

        return list(movies_map.values())

    def query_by_director(self, director: str = "") -> dict:
        print(f"[INFO] Procurando por filmes do diretor: {director}")

        # 1. Pega foto do diretor
        person_image = self.tmdb.get_person_image(director)

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
        movie_list = []

        for row in query_return:
            actors_str = str(row.actors) if getattr(row, 'actors', None) else ""
            actors_list = [a.strip() for a in actors_str.split(',')] if actors_str else []
            
            movie_title = str(row.Movies)
            # Busca dados completos do filme
            tmdb_data = self.tmdb.get_movie_data(movie_title)

            movie_list.append({
                "movie_title": movie_title,
                "poster": tmdb_data.get("poster"),
                "rating": tmdb_data.get("rating"),
                "overview": tmdb_data.get("overview"),
                "actors": actors_list
            })

        return {
            "person_image": person_image,
            "movies": movie_list
        }