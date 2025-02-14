import os
import click
import requests
from tabulate import tabulate
from bs4 import BeautifulSoup
from collections import defaultdict
steam_key = os.environ['steam_key']

USER_INFO = {"ready_for_data": True}

def get_id(username):
    if username.isnumeric():
        return username
    else:
        user_id_url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={steam_key}&vanityurl={username}"
        find_id = requests.get(user_id_url)
        user_id = find_id.json()['response']['steamid']
        return user_id


def get_games(USER_ID):
    games_url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_key}&steamid={USER_ID}&format=json"
    games_request = requests.get(games_url)
    all_games = games_request.json()['response']['games']
    games_list = [{"id": game['appid'], "time": game['playtime_forever']} for game in all_games]
    sorted_games = sorted(games_list, key=lambda x: x['time'], reverse=True)
    top_games = sorted_games[0:15]
    return top_games


def get_game_info(list):
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
        games.append({'key': key, 'id': game['id'], 'title': game_name.text, 'url': game_url, "time":game['time'],
                      'tags': tags, 'genres': genres})

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
    return_games = [{"id":game,"time":0} for game in new_game_ids]
    return return_games


def top_new_games(owned_games,games,tags):
    new_games = []
    for game in games:
        games_tags= list(set(game['tags']) & set(tags))
        new_games.append({"title":game['title'],"id":game['id'], "tags":games_tags})
    sorted_games = sorted(new_games, key=lambda x: len(x['tags']), reverse=True)
    owned_simplified = [game['id'] for game in owned_games]
    return_games = [game for game in sorted_games if game['id'] not in owned_simplified]
    return return_games[0:15]

@click.command()
@click.argument("username", required=False)
@click.option("--verbose", is_flag=True, help="Enable detailed output")
def main(username, verbose):
    if not username:
        username = click.prompt("Enter your Steam username or ID")
    user_id = get_id(username)
    if not user_id:
        click.secho("Error: Could not resolve Steam ID. Check the username.", fg="red", bold=True)
        return
    click.secho(f"Fetching data for user: {username}...", fg="cyan")
    games = get_games(user_id)
    game_info = get_game_info(games)
    game_table = [[game['title'], f"{round(int(game['time']) / 60)}hrs played"]for game in game_info]
    click.secho("\nYour Top 15 Games:", fg="green", bold=True)
    click.secho(tabulate(game_table))
    tags = favorite_tags(game_info)
    click.secho("\nYour Top 10 Tags:", fg="yellow", bold=True)
    tags_table = [[tag, f"{number} games"] for tag, number in tags.items()]
    click.secho(tabulate(tags_table))
    new_game_suggestions = new_games(game_info)
    new_games_info = get_game_info(new_game_suggestions)
    suggested_games = top_new_games(game_info,new_games_info,tags)
    suggested_games_table = [[game['title'], ", ".join(game['tags'])] for game in suggested_games]
    print(tabulate(suggested_games_table))

if __name__ == "__main__":
    main()