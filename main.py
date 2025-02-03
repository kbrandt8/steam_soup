import os

import requests
from bs4 import BeautifulSoup

steam_key = os.environ['steam_key']

SUGGESTED_GAMES = {"ready_for_data": True, "games": []}


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


def get_tags(games_list):
    game_tags = []
    for game in games_list:
        game_url = f"https://store.steampowered.com/app/{game['id']}/"
        get_game_data = requests.get(game_url)
        soup = BeautifulSoup(get_game_data.content, "html.parser")
        game_info = soup.find_all('a', attrs={'class': 'app_tag'})
        for link in game_info:
            game_tags.append({'tag': link.text.strip(), 'url': link['href']})
    return game_tags


while SUGGESTED_GAMES['ready_for_data']:
    user = input("Please input your Steam Username or id:\n")
    print("Getting user info...")
    USER_ID = get_id(user)
    print("Accessing User game list...")
    games = get_games(USER_ID)
    print("Finding all game tags...")
    all_game_tags = get_tags(games)
    print(all_game_tags)

    SUGGESTED_GAMES.update({"ready_for_data": False})
