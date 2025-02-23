import requests
from bs4 import BeautifulSoup

from utils import progress_bar


@progress_bar()
def get_game_info(games:list[dict[str,int]], bar=None, label="")-> list[dict[str,list[str]]]:
    """Scrapes Steam Store to retrieve name, tags, and genres for a given list of games."""
    scraped_games = []

    for key, game in enumerate(games):
        game_url = f"https://store.steampowered.com/app/{game['id']}/"
        try:
            response = requests.get(game_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            game_genres = soup.find('div', attrs={'id': 'genresAndManufacturer'})
            game_name = soup.find('div', attrs={'id': 'appHubAppName_responsive'}).text

            genres = [genre.text.strip() for genre in game_genres.find_all('span')]
            tags = [tag.text.strip() for tag in soup.find_all('a', attrs={'class': 'app_tag'})]

            scraped_games.append(
                {'key': key, 'id': game['id'], 'title': game_name, 'url': game_url, "time": game.get("time", 0),
                 'tags': tags, 'genres': genres})
            if bar:
                bar.update(1)

        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch data for game ID {game['id']}: {e}")  # 🔥 Stops execution

        if not scraped_games:
            raise ValueError("No valid game data found.")  # 🔥 Prevents returning an empty list

    return scraped_games


@progress_bar()
def new_games(games:list[dict[str,list[str]]], bar=None, label="")->list[dict[str,int]]:
    """Finds the games marked as similar to any list of games."""
    new_game_ids = []
    for game in games:
        game_url = f"https://store.steampowered.com/recommended/morelike/app/{game['id']}/"
        soup = BeautifulSoup(requests.get(game_url).content, "html.parser")
        similar_games = [int(game['data-ds-appid']) for game in
                         soup.find_all('a', attrs={'class': 'similar_grid_capsule'})[0:9]]
        bar.update(1)
        similar_games_sorted = [game for game in similar_games if game not in new_game_ids]

        new_game_ids.extend(similar_games_sorted)

    return_games = [{"id": game} for game in new_game_ids]

    return return_games
