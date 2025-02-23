import functools
import os
from collections import defaultdict

import click
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tabulate import tabulate

from steam_user import SteamUser

load_dotenv()
STEAM_KEY = os.environ['STEAM_KEY']


def progress_bar(length=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            label = kwargs.get("label", "Processing...")

            iterable = args[0] if args else kwargs.get("data", [])
            total = length or len(iterable)

            fill_char = click.style("♥", fg="red")
            empty_char = click.style("♡", fg="white", dim=True)

            with click.progressbar(length=total, label=label, fill_char=fill_char, empty_char=empty_char) as bar:
                return func(*args, **kwargs, bar=bar)  # Pass progress bar to function

        return wrapper

    return decorator


def get_games(USER_ID):
    games_url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_KEY}&steamid={USER_ID}&format=json"
    games_request = requests.get(games_url)
    all_games = games_request.json()['response']['games']
    games_list = [{"id": game['appid'], "time": game['playtime_forever']} for game in all_games]
    sorted_games = sorted(games_list, key=lambda x: x['time'], reverse=True)
    top_games = sorted_games[0:15]
    return top_games


@progress_bar()
def get_game_info(list, bar=None, label=""):
    games = []

    for key, game in enumerate(list):
        game_url = f"https://store.steampowered.com/app/{game['id']}/"
        get_game_data = requests.get(game_url)
        soup = BeautifulSoup(get_game_data.content, "html.parser")
        game_tags = soup.find_all('a', attrs={'class': 'app_tag'})
        game_genres = soup.find('div', attrs={'id': 'genresAndManufacturer'})
        all_genres = game_genres.find_all('span')
        genres = []
        for genre in all_genres:
            text = genre.text
            new_list = text.split(",")
            for item in new_list:
                genres.append(item.strip())

        game_name = soup.find('div', attrs={'id': 'appHubAppName_responsive'})
        tags = []
        for tag in game_tags:
            tags.append(tag.text.strip())
        games.append({'key': key, 'id': game['id'], 'title': game_name.text, 'url': game_url, "time": game['time'],
                      'tags': tags, 'genres': genres})
        bar.update(1)

    return games


def favorite_tags(games_list):
    tag_counts = defaultdict(int)
    for game in games_list:
        for tag in game['tags']:
            tag_counts[tag] += 1
    sorted_tally = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
    return dict(sorted_tally[0:10])


def new_games(games):
    new_game_ids = []
    for game in games:
        game_url = f"https://store.steampowered.com/recommended/morelike/app/{game['id']}/"
        get_game_data = requests.get(game_url)
        soup = BeautifulSoup(get_game_data.content, "html.parser")
        new_games = soup.find_all('a', attrs={'class': 'similar_grid_capsule'})
        for game in new_games[0:9]:
            id = int(game['data-ds-appid'])
            if id not in new_game_ids:
                new_game_ids.append(id)
    return_games = [{"id": game, "time": 0} for game in new_game_ids]
    return return_games


@progress_bar()
def top_new_games(owned_games, games, tags, bar=None, label=""):
    new_games = []
    for game in games:
        games_tags = list(set(game['tags']) & set(tags))
        new_games.append({"title": game['title'], "id": game['id'], "tags": games_tags})
        bar.update(1)
    sorted_games = sorted(new_games, key=lambda x: len(x['tags']), reverse=True)
    bar.update(5)
    owned_simplified = [game['id'] for game in owned_games]
    bar.update(5)
    return_games = [game for game in sorted_games if game['id'] not in owned_simplified]
    bar.update(5)

    return return_games[0:15]


@click.command()
@click.argument("username", required=False)
@click.option("--clear-cache", is_flag=True, help="Delete cached user data and fetch fresh data")
def main(username, clear_cache):
    if not username:
        username = click.prompt("Enter your Steam username or ID")

    user = SteamUser(username)

    if not user.user_id:
        click.secho("Error: Could not resolve Steam ID. Check the username.", fg="red", bold=True)
        return

    if clear_cache and os.path.exists(user.user_file_path):
        user.clear_cache()

    if os.path.exists(user.user_file_path):
        user.use_saved_user()

    else:
        click.secho(f"Fetching data for user: {username}...", fg="cyan")
        games = get_games(user.user_id)
        user.top_games = get_game_info(games, label="Getting info on games list...")
        game_table = [[game['title'], f"{round(int(game['time']) / 60)}"] for game in user.top_games]
        click.secho("\nYour Top 15 Games:", fg="green", bold=True)
        click.secho(tabulate(game_table, tablefmt="fancy_grid", headers=['Game Title', 'Hours Played']))
        user.top_tags = favorite_tags(user.top_games)
        click.secho("\nYour Top 10 Tags:", fg="yellow", bold=True)
        tags_table = [[tag, f"{number}"] for tag, number in user.top_tags.items()]
        click.secho(tabulate(tags_table, tablefmt="fancy_grid", headers=['Tag', '# of Games with Tag']))
        user.save_user()

    new_game_suggestions = new_games(user.top_games)
    new_games_info = get_game_info(new_game_suggestions, label="Getting info on game suggestions...")
    user.user_recommendations = top_new_games(user.top_games, new_games_info, user.top_tags,
                                              label="Sorting game suggestions...")
    suggested_games_table = [[game['title'], "\n ".join(game['tags'])] for game in user.user_recommendations]
    click.secho(
        tabulate(suggested_games_table, tablefmt="fancy_grid", headers=['Game Title', 'Tags from your Top Tags']))
    user.save_recommendations()


if __name__ == "__main__":
    main()
