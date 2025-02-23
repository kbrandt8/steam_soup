import os
import webbrowser

import click
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
STEAM_KEY = os.getenv("STEAM_KEY")
# Steam API Key registration page
steam_api_url = "https://steamcommunity.com/dev/apikey"

if not STEAM_KEY:
    click.secho("\n🚨 STEAM_KEY not found in environment variables! 🚨", fg="red", bold=True)
    # Attempt to open the Steam API Key page in the default browser
    click.secho("\nOpening the Steam API Key registration page in your browser...", fg="cyan")
    webbrowser.open(steam_api_url)
    # Provide a clickable link for users who prefer to open it manually
    click.secho(f"\nIf the page did not open, visit this link manually:\n🔗 {steam_api_url}\n", fg="blue", bold=True)
    # Save the key to the .env file
    if click.confirm("Would you like to input your Steam API key now?"):
        steam = click.prompt("Steam Key")
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"STEAM_KEY={steam}")
        click.secho("✅ STEAM_KEY saved to .env file!", fg="green")
        STEAM_KEY = steam
    else:
        raise ValueError("\n❌ Error: STEAM_KEY is required but was not provided.")
