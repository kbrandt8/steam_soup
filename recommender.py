from collections import defaultdict

from utils import progress_bar


def favorite_tags(games_list: list[dict[str, any]]) -> dict[str, int]:
    """Creates a tally for users tags, and sorts them by most often seen in favorite games"""
    tag_counts = defaultdict(int)

    for game in games_list:
        for tag in game['tags']:
            tag_counts[tag] += 1

    sorted_tally = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
    return dict(sorted_tally[0:10])  # Only returns top 10 tags


@progress_bar()
def top_new_games(owned_games: list[str, any],
                  games: list[str, list],
                  tags: dict[str, int], bar=None, label="") \
        -> list[dict[str, list]]:
    """Sorts games by how many of the users favorite tags it has."""
    owned_game_ids = [game['id'] for game in owned_games]
    if bar:
        bar.update(5)
    ranked_games = [
        {"title": game['title'], "id": game['id'], "tags": list(set(game['tags']) & set(tags))}
        for game in games]
    if bar:
        bar.update(5)
    sorted_games = sorted(ranked_games, key=lambda x: len(x['tags']), reverse=True)
    if bar:
        bar.update(5)

    return [game for game in sorted_games if game['id'] not in owned_game_ids][:15]  # Exclude owned games
