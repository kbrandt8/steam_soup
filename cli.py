import os

import click

from cli_helpers import fetch_user_data, generate_game_recommendations, display_top_games
from steam_user import SteamUser
from utils import welcome_message


@click.command()
@click.argument("username", required=False)
@click.option("--clear-cache", is_flag=True, help="Delete cached user data and fetch fresh data")
@click.option("--top-games-tags", is_flag=True, help="View your most played games and tags from your steam library.")
@click.option("--game-recs", is_flag=True, help="Retrieve game recommendations based on your steam data")
def main(username, clear_cache, game_recs, top_games_tags):
    """Main CLI function to fetch and display Steam user data."""
    welcome_message()
    # Prompt user for username if nort provided.
    if not username:
        username = click.prompt("Enter your Steam username or ID")

    user = SteamUser(username)

    # Handle invalid usernames
    if not user.user_id:
        click.secho("❌ Error: Could not resolve Steam ID. Check the username.", fg="red", bold=True)
        return

    # Clears Json data if clear cache is requested
    if clear_cache and os.path.exists(user.user_file_path):
        user.clear_cache()

    # Fetch user data from json or from Steam Api
    fetch_user_data(user)

    # Display most played games and tags if requested
    if top_games_tags:
        display_top_games(user)

    # Generate and display game recommendations if requested
    if game_recs:
        generate_game_recommendations(user)

