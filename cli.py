import os

import click

from cli_helpers import fetch_user_data, generate_game_recommendations, display_top_games,get_saved_users,welcome_message,display_menu
from steam_user import SteamUser


@click.command()
@click.argument("username", required=False)
@click.option("--clear-cache", is_flag=True, help="Delete cached user data and fetch fresh data")
@click.option("--top-games-tags", is_flag=True, help="View your most played games and tags from your steam library.")
@click.option("--game-recs", is_flag=True, help="Retrieve game recommendations based on your steam data")
def main(username, clear_cache, game_recs, top_games_tags):
    """Main CLI function to fetch and display Steam user data."""
    welcome_message()

    if not username:
        username = get_saved_users()

    # Prompt user for username if not provided.
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

    while True:
        display_menu(user)
        selection= int(click.prompt("Enter selection"))
        if selection == 3:
            click.secho("\n👋 Exiting Steam Soup. Have a great day! 🎮", fg="magenta", bold=True)
            break
        elif selection == 2:
            generate_game_recommendations(user)
        elif selection == 1:
            display_top_games(user)
        click.pause("\n⏳ Press Enter to continue...\n")  # Prevents auto-restarting instantly


