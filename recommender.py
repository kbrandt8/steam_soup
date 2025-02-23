from collections import defaultdict

from utils import progress_bar


def favorite_tags(games_list):
    tag_counts = defaultdict(int)
    for game in games_list:
        for tag in game['tags']:
            tag_counts[tag] += 1
    sorted_tally = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
    return dict(sorted_tally[0:10])


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
