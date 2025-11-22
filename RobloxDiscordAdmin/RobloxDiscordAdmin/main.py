import discord
from discord.ext import commands
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Set API_URL to your Render service public URL
API_URL = os.getenv("API_URL")  # Example: https://myflaskapi.onrender.com

@bot.command()
async def startsession(ctx, *, session_name: str):
    response = requests.post(f"{API_URL}/start-session", json={"session_name": session_name})
    if response.status_code == 200:
        session = response.json()['session']
        await ctx.send(f"✅ Session started!\nID: `{session['session_id']}`\nName: `{session['session_name']}`")
    else:
        await ctx.send(f"❌ Failed: {response.json()}")

@bot.command()
async def stopsession(ctx, session_id: str):
    response = requests.post(f"{API_URL}/stop-session", json={"session_id": session_id})
    if response.status_code == 200:
        await ctx.send(f"✅ Session {session_id} stopped!")
    else:
        await ctx.send(f"❌ Failed: {response.json()}")

@bot.command()
async def getsession(ctx, session_id: str):
    response = requests.get(f"{API_URL}/get-session/{session_id}")
    if response.status_code == 200:
        await ctx.send(f"ℹ️ Session info: ```json\n{json.dumps(response.json(), indent=2)}\n```")
    else:
        await ctx.send(f"❌ Not found.")

@bot.command()
async def listsessions(ctx):
    response = requests.get(f"{API_URL}/list-sessions")
    if response.status_code == 200:
        await ctx.send(f"📄 All sessions: ```json\n{json.dumps(response.json(), indent=2)}\n```")
    else:
        await ctx.send(f"❌ Failed: {response.json()}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    print("Bot ready!")

bot.run(DISCORD_BOT_TOKEN)
