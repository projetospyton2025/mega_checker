import requests

def fetch_results(draw=None):
    url = "https://api.guidi.dev.br/loteria/megasena/"
    url += str(draw) if draw else "ultimo"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None
