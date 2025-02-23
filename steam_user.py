import json
import os
from collections import defaultdict
import click

import requests
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
STEAM_KEY = os.environ['STEAM_KEY']


class SteamUser:
    """Handles user data from the Steam API, including fetching games and saving/loading user info."""

    def __init__(self, username):
        self.username = username
        self.user_id = self.get_steam_id()
        self.top_games=[]
        self.top_tags = {}
        self.user_recommendations=[]
        self.user_file_path = f"{self.user_id}_user_info.json"
        self.user_rec_path = f"{self.user_id}_recommendations"

    def get_steam_id(self):
        """Retrieve the Steam ID"""
        if self.username.isnumeric():
            return self.username  # It's already the ID from the prompt
        else:

            url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={STEAM_KEY}&vanityurl={self.username}"
            try:
                response = requests.get(url).json()
                return response['response'].get('steamid', None)

            except(requests.RequestException, KeyError):
                click.secho("Error: Failed to retrieve Steam ID.",fg="red")
                return None

    def save_user(self):
        """Save user data to a local JSON file for later use."""
        filename = f"{self.user_id}_user_info.json"
        data = {
            "user": self.username,
            "id": self.user_id,
            "top_tags": self.top_tags,
            "top_games": self.top_games
        }
        try:
            with open(self.user_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return self.user_file_path
        except IOError:
            click.secho("Error:Failed to save user data.",fg="red")

    def use_saved_user(self):
        """Load previously saved user data if available."""
        if not os.path.exists(self.user_file_path):
            click.secho("No saved user data found.",fg="cyan")
            return None
        try:
            with open(self.user_file_path, 'r') as f:
                data = json.load(f)
                self.user_id = data.get("id",)
                self.username = data.get("user")
                self.top_games = data.get("top_games")
                self.top_tags = data.get("top_tags")
        except (IOError,json.JSONDecodeError):
            click.secho("Error: Failed to load saved user data.",fg="red")

    def clear_cache(self):
        """Delete saved user data and recommendations"""
        try:
            if os.path.exists(self.user_file_path):
                os.remove(self.user_file_path)
                click.secho("Deleted user data", fg="white")
            if os.path.exists(self.user_rec_path):
                os.remove(self.user_rec_path)
        except OSError:
            click.secho("Error:failed to delete cache files.",fg="red")

    def save_recommendations(self):
        """Save user recommendations to a local JSON file for later use."""
        try:
            with open(self.user_rec_path, "w", encoding="utf-8") as f:
                json.dump(self.user_recommendations, f, indent=4)
            click.secho(f"View results in {self.user_rec_path}")
        except (IOError,json.JSONDecodeError):
            click.secho("Error: Failed to save recommendations.",fg="red")
