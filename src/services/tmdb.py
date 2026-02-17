from dotenv import load_dotenv
import requests
import os

load_dotenv()

class TMDb:
    def __init__(self):
        self.TOKEN = os.getenv("API_TOKEN")
        self.KEY = os.getenv("API_KEY")
        self.QUERY_URL = "https://api.themoviedb.org/3/search/movie?query="
        self.POSTER_ROOT = "https://image.tmdb.org/t/p/w500"

    def get_poster(self, movie_name: str, year: str = ""):
        poster_url = self.QUERY_URL + movie_name + "&year=" + year if year else self.QUERY_URL + movie_name

        try:
            response = requests.get(url=poster_url, headers={"Authorization": f"Bearer {self.TOKEN}"})
            data = response.json()
        except Exception as e:
            print(f"[ERROR] Falha de requisição TMDb: {e}")
            return None

        results = data.get("results", []) or []
        if not isinstance(results, list) or len(results) == 0:
            print(f"[WARN] TMDb não encontrou resultados para: '{movie_name}': {data}")
            return None

        first = results[0]
        poster_location = first.get("poster_path") if isinstance(first, dict) else None
        if not poster_location:
            print(f"[WARN] Nenhum poster encontrado para: '{movie_name}': {first}")
            return None

        poster_path = self.POSTER_ROOT + poster_location

        print(f"[INFO] Requisição para TMDb: {data}")
        return poster_path