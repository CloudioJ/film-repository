from dotenv import load_dotenv
import requests
import os

load_dotenv()

class TMDb:
    def __init__(self):
        self.TOKEN = os.getenv("API_TOKEN")
        # Base da URL para imagens (w500 é um tamanho bom, original é full size)
        self.IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
        self.BASE_URL = "https://api.themoviedb.org/3"
        
        # Headers padrão para autenticação
        self.headers = {
            "Authorization": f"Bearer {self.TOKEN}",
            "accept": "application/json"
        }

    def get_person_image(self, name: str):
        """Busca a foto de perfil de um ator ou diretor."""
        if not name: 
            return None
            
        url = f"{self.BASE_URL}/search/person"
        params = {
            "query": name,
            "language": "pt-BR"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()
            
            if data.get('results'):
                path = data['results'][0].get('profile_path')
                if path:
                    return f"{self.IMAGE_BASE}{path}"
            return None
        except Exception as e:
            print(f"[ERRO TMDb Person] {e}")
            return None

    def get_movie_data(self, movie_name: str, year: str = ""):
        """Busca Poster, Sinopse (PT-BR) e Nota do filme."""
        if not movie_name:
            return {}

        url = f"{self.BASE_URL}/search/movie"
        params = {
            "query": movie_name,
            "language": "pt-BR", # <--- O SEGREDO DA TRADUÇÃO
            "include_adult": "false"
        }
        if year:
            params["year"] = year

        try:
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()
            results = data.get("results", [])

            if not results:
                print(f"[WARN] Filme não encontrado no TMDb: {movie_name}")
                return {} # Retorna dicionário vazio se não achar

            first = results[0]
            
            # Monta o objeto com tudo que você pediu
            poster_path = first.get("poster_path")
            
            return {
                "poster": f"{self.IMAGE_BASE}{poster_path}" if poster_path else None,
                "overview": first.get("overview", "Sinopse indisponível."),
                "rating": first.get("vote_average", 0), # A nota (ex: 7.5)
                "release_date": first.get("release_date", "")
            }

        except Exception as e:
            print(f"[ERRO TMDb Movie] {e}")
            return {}