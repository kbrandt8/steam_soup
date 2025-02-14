import os

import requests
from bs4 import BeautifulSoup

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
        games.append({'key': key, 'id': game['id'], 'title': game_name.text, 'url': game_url,
                      'tags': tags, 'genres': genres})

    return games


def get_tags(games_list):
    all_tags = []
    for game in games_list:
        for tag in game['tags']:
            all_tags.append(tag)
    return all_tags


def favorite_tags(tag_list):
    tags_tally = {}
    for tag in tag_list:
        if tag in tags_tally:
            tags_tally[tag] += 1
        else:
            tags_tally[tag] = 1
    sorted_tally = sorted(tags_tally.items(), key=lambda item: item[1], reverse=True)
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
    return_games = [{"id":game} for game in new_game_ids]
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


while USER_INFO['ready_for_data']:
    user = input("Please input your Steam Username or id:\n")
    print("Getting user info...")
    USER_INFO['id'] = get_id(user)
    print("Accessing User game list...")
    games = get_games(USER_INFO['id'])
    print("Getting Game Info...")
    USER_INFO['fave_games'] = get_game_info(games)
    game_titles = [game['title'] for game in USER_INFO['fave_games']]
    print(f"\nYour Top 15 games: \n-  {"\n-  ".join(game_titles)}\n")
    print("Finding all game tags...")
    all_game_tags = get_tags(USER_INFO['fave_games'])
    print("Tallying tags...")
    USER_INFO['tags'] = favorite_tags(all_game_tags)
    print(f"\nYour Top Ten tags: \n-  {'\n-  '.join(list(USER_INFO['tags'].keys()))}\n")
    print("Finding games based on your favorites...")
    new_game_suggestions = new_games(USER_INFO['fave_games'])
    print("Finding information on your suggestions...")
    new_games_info = get_game_info(new_game_suggestions)
    print("Ranking your suggestions...")
    USER_INFO['suggested_games'] = top_new_games(USER_INFO['fave_games'],new_games_info,USER_INFO['tags'])
    suggested_games_titles= [game['title'] for game in USER_INFO['suggested_games']]
    print(f"\nYour Top 15 suggested games: \n-  {"\n-  ".join(suggested_games_titles)}\n")
    USER_INFO.update({"ready_for_data": False})
