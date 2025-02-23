import os

import click
from tabulate import tabulate

from recommender import favorite_tags, top_new_games
from scraper import get_game_info, new_games
from steam_user import SteamUser


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
        if not user.use_saved_user():
            return

    else:
        click.secho(f"Fetching data for user: {username}...", fg="cyan")
        user.get_owned_games()
        user.top_games = get_game_info(user.owned_games, label="Getting info on games list...")

        game_table = [[game['title'], f"{round(int(game['time']) / 60)}"] for game in user.top_games]
        click.secho("\nYour Top 15 Games:", fg="green", bold=True)
        click.secho(tabulate(game_table, tablefmt="fancy_grid", headers=['Game Title', 'Hours Played']))

        user.top_tags = favorite_tags(user.top_games)
        click.secho("\nYour Top 10 Tags:", fg="yellow", bold=True)
        tags_table = [[tag, f"{number}"] for tag, number in user.top_tags.items()]
        click.secho(tabulate(tags_table, tablefmt="fancy_grid", headers=['Tag', '# of Games with Tag']))
        user.save_user()

    new_game_suggestions = new_games(user.top_games,"Finding games similar to your favorites...")
    new_games_info = get_game_info(new_game_suggestions, label="Getting info on game suggestions...")
    user.user_recommendations = top_new_games(user.top_games, new_games_info, user.top_tags,
                                              label="Sorting game suggestions...")
    suggested_games_table = [[game['title'], "\n ".join(game['tags'])] for game in user.user_recommendations]
    click.secho(
        tabulate(suggested_games_table, tablefmt="fancy_grid", headers=['Game Title', 'Tags from your Top Tags']))
    user.save_recommendations()


if __name__ == "__main__":
    main()
