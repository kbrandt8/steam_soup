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


def get_game_info(list):
    games = []
    for key, game in enumerate(list):
        game_url = f"https://store.steampowered.com/app/{game['id']}/"
        get_game_data = requests.get(game_url)
        soup = BeautifulSoup(get_game_data.content, "html.parser")
        game_tags = soup.find_all('a', attrs={'class': 'app_tag'})
        game_genres = soup.find('div', attrs={'id':'genresAndManufacturer'})
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
            tags.append({'title': tag.text.strip(), 'url': tag['href']})
        games.append({'key': key, 'id': game['id'], 'title': game_name.text, 'url': game_url, 'time': game['time'],
                      'tags': tags,'genres':genres})

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

def get_genres(games_list):
    all_genres = []
    for game in games_list:
        for genre in game['genres']:
            all_genres.append(genre)
    return all_genres

def get_top_genres(genres):
    genre_tally = {}
    for genre in genres:
        if genre in genre_tally:
            genre_tally[genre] +=1
        else:
            genre_tally[genre] = 1

    sorted_tally = sorted(genre_tally.items(), key=lambda item: item[1], reverse=True)
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


while SUGGESTED_GAMES['ready_for_data']:
    user = input("Please input your Steam Username or id:\n")
    print("Getting user info...")
    USER_ID = get_id(user)
    print("Accessing User game list...")
    games = get_games(USER_ID)
    print("Getting Game Info...")
    games_info = get_game_info(games)
    game_titles = []
    for game in games_info:
        game_titles.append(game['title'])
    print(f"\nYour Top 15 games: \n-  {"\n-  ".join(game_titles)}\n")
    print("Finding all game tags...")
    all_game_tags = get_tags(games_info)
    print("Tallying tags...")
    tags = favorite_tags(all_game_tags)
    print(f"\nYour Top Ten tags: \n-  {'\n-  '.join(list(tags.keys()))}\n")
    all_genres = get_genres(games_info)
    genres = get_top_genres(all_genres)
    print(f"\nYour Top Ten Genres: \n-  {'\n-  '.join(list(genres.keys()))}\n")
    new_game_suggestions = new_games(games_info)
    print("Finding games based on your favorites...")
    new_games_info = get_game_info(new_game_suggestions)
    print("Finding information on your suggestions...")
    suggested_games = top_new_games(games_info,new_games_info,tags)
    print("Ranking your suggestions...")
    suggested_games_titles= [game['title'] for game in suggested_games]
    print(f"\nYour Top 15 suggested games: \n-  {"\n-  ".join(suggested_games_titles)}\n")


    SUGGESTED_GAMES.update({"ready_for_data": False})
