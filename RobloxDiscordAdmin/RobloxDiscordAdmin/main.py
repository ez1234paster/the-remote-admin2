import discord
from discord.ext import commands
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the Discord bot token from the environment variable
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Initialize the Discord bot
bot = commands.Bot(command_prefix="!")

# Roblox configuration (example)
ROBOX_API_URL = "http://localhost:5000"  # URL to your Flask API running locally or on the web
ROBLOX_SESSION_KEY = "your_roblox_session_key"  # API key or session token (if needed)


# Example of Roblox Game Function
def get_roblox_player_info(player_name):
    """Fetch player data from Roblox API"""
    response = requests.get(f"{ROBOX_API_URL}/player/{player_name}",
                            headers={"Authorization": f"Bearer {ROBLOX_SESSION_KEY}"})

    if response.status_code == 200:
        return response.json()  # Return the player data as JSON
    else:
        return None  # Handle error if player data cannot be fetched


# Discord command to get Roblox player info
@bot.command()
async def roblox(ctx, player_name: str):
    """Command to get player info from Roblox"""
    player_info = get_roblox_player_info(player_name)

    if player_info:
        await ctx.send(f"Player Info: {json.dumps(player_info, indent=2)}")  # Format the JSON data
    else:
        await ctx.send(f"Could not fetch data for player {player_name}.")


# Command to create a session (initiates Roblox interaction and creates a forum)
@bot.command()
async def startsession(ctx):
    """Create a session and create a forum channel for it"""

    # Send a request to Flask API to create a session
    response = requests.post(f"{ROBOX_API_URL}/start-session",
                             json={"session_id": "session123", "session_name": "Test Session"})

    if response.status_code == 200:
        session_data = response.json()  # Assuming the session response contains data like session ID, player names, etc.
        session_id = session_data.get('session_id', 'Unknown')
        session_name = session_data.get('session_name', 'Unknown')

        # Create a new channel in the server for the session
        guild = ctx.guild  # Get the current server (guild)

        # Create the channel to track this session (assuming the session name is descriptive)
        session_channel = await guild.create_text_channel(f"session-{session_id}",
                                                          category=None)  # Optionally, assign to a specific category

        # Send the session info to the new channel
        await session_channel.send(f"Session started: {session_name} (ID: {session_id})")

        # Optionally, post more details about the session
        await session_channel.send(f"Session info: {json.dumps(session_data, indent=2)}")

        await ctx.send(f"Session '{session_name}' started successfully and posted to {session_channel.mention}!")
    else:
        await ctx.send("Failed to start session! Please try again later.")


# Command to stop the session
@bot.command()
async def stopsession(ctx):
    """Stop the current session"""
    response = requests.post(f"{ROBOX_API_URL}/stop-session", json={"session_id": "session123"})

    if response.status_code == 200:
        await ctx.send("Session stopped successfully!")
    else:
        await ctx.send("Failed to stop session!")


# Run the bot
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')


bot.run(DISCORD_BOT_TOKEN)
