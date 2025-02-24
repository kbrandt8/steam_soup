import os

import click
from tabulate import tabulate

from recommender import favorite_tags, top_new_games
from scraper import get_game_info, new_games


def fetch_user_data(user):
    """Fetch and store user top played games and top tags if no json data is found"""
    if os.path.exists(user.user_file_path):
        user.use_saved_user()
    else:
        click.secho(f"Fetching data for user: {user.username}...", fg="cyan")
        user.get_owned_games()
        user.top_games = get_game_info(user.owned_games, label="Getting info on games list...")
        user.top_tags = favorite_tags(user.top_games)
        click.secho("✅ Your information and top games have been recorded for later use.", fg="green")
        user.save_user()


def generate_game_recommendations(user):
    """Find and display game recommendations based on user's top tags."""
    new_game_suggestions = new_games(user.top_games, label="🔎 Finding games similar to your favorites...")
    new_games_info = get_game_info(new_game_suggestions, label="📖 Getting info on game suggestions...")
    user.user_recommendations = top_new_games(user.top_games, new_games_info, user.top_tags,
                                              label="🎯 Sorting game suggestions...")
    suggested_games_table = [[game['title'], "\n".join(game['tags'])] for game in user.user_recommendations]
    click.secho("\n🕹️ Recommended Games for You:", fg="blue", bold=True)
    click.secho(
        tabulate(suggested_games_table, tablefmt="fancy_grid", headers=['Game Title', 'Tags from your Top Tags']))
    user.save_recommendations()


def display_top_games(user):
    """Display the user's most played games and most frequent tags."""
    game_table = [[game['title'], f"{round(int(game['time']) / 60)}"] for game in user.top_games]

    click.secho("\n🎮 Your Top 15 Games:", fg="green", bold=True)
    click.secho(tabulate(game_table, tablefmt="fancy_grid", headers=['Game Title', 'Hours Played']))

    tags_table = [[tag, f"{number}"] for tag, number in user.top_tags.items()]

    click.secho("\n🏷️ Your Top 10 Tags:", fg="yellow", bold=True)
    click.secho(tabulate(tags_table, tablefmt="fancy_grid", headers=['Tag', '# of Games with Tag']))
