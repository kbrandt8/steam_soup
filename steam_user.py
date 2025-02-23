import json
import os

import click
import requests
from config import STEAM_KEY


class SteamUser:
    """Handles user data from the Steam API, including fetching games and saving/loading user info."""

    def __init__(self, username):
        self.username = username
        self.user_id = self.get_steam_id()
        self.owned_games = []
        self.top_games = []
        self.top_tags = {}
        self.user_recommendations = []
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
                return None

    def get_owned_games(self):
        """Fetch the user's top 15 most-played games from the Steam API."""
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_KEY}&steamid={self.user_id}&format=json"
        try:
            response = requests.get(url).json()
            all_games = response['response'].get('games', [])

            # Extract game IDs and playtime, then sort by playtime
            self.owned_games = sorted(
                [{"id": g["appid"], "time": g["playtime_forever"]} for g in all_games],
                key=lambda x: x["time"],
                reverse=True
            )[:15]
        except (requests.RequestException, KeyError):
            print("Error: Failed to retrieve owned games.")
            self.owned_games = []

    def save_user(self):
        """Save user data to a local JSON file for later use."""
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
            click.secho("Error: Failed to save user data.", fg="red")

    def use_saved_user(self):
        """Load previously saved user data if available."""
        if not os.path.exists(self.user_file_path):
            raise ValueError("No saved user data found.")
        try:
            with open(self.user_file_path, 'r') as f:
                data = json.load(f)
                self.user_id = data.get("id")
                self.username = data.get("user")
                self.top_games = data.get("top_games")
                self.top_tags = data.get("top_tags")
            if not self.top_games or not self.top_tags:
                raise ValueError("Saved data is incomplete (missing games or tags).")
        except (IOError, json.JSONDecodeError):
            raise ValueError("Error: Failed to load saved user data.")
        except ValueError as e:
            raise ValueError(f"Error: {e} \n Try again with --clear-cache for new information")


    def clear_cache(self):
        """Delete saved user data and recommendations"""
        try:
            if os.path.exists(self.user_file_path):
                os.remove(self.user_file_path)
                click.secho("Deleted user data", fg="white")
            if os.path.exists(self.user_rec_path):
                os.remove(self.user_rec_path)
        except OSError:
            click.secho("Error:failed to delete cache files.", fg="red")

    def save_recommendations(self):
        """Save user recommendations to a local JSON file for later use."""
        try:
            with open(self.user_rec_path, "w", encoding="utf-8") as f:
                json.dump(self.user_recommendations, f, indent=4)
            click.secho(f"View results in {self.user_rec_path}")
        except (IOError, json.JSONDecodeError):
            click.secho("Error: Failed to save recommendations.", fg="red")
