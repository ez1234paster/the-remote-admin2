import discord
from discord.ext import commands, tasks
from flask import Flask, request, jsonify
from threading import Thread
import uuid
import requests
import os
from dotenv import load_dotenv

# ---------------- Load .env ----------------
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("API_URL")  # Your own Render URL if needed, or leave for internal use

# ---------------- Flask API ----------------
app = Flask(__name__)

# Store sessions
sessions = {}

@app.route('/create-session', methods=['POST'])
def create_session():
    data = request.json
    game_id = data.get("game_id")
    player_name = data.get("player_name")

    if not game_id or not player_name:
        return jsonify({"status": "error", "message": "game_id and player_name required"}), 400

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "session_id": session_id,
        "game_id": game_id,
        "player_name": player_name
    }

    # Optional: notify Discord bot or forum here

    return jsonify({"status": "success", "session": sessions[session_id]}), 200

@app.route('/list-sessions', methods=['GET'])
def list_sessions():
    return jsonify(sessions), 200

def run_flask():
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ---------------- Discord Bot ----------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def listsessions(ctx):
    if sessions:
        await ctx.send(f"📄 All sessions: ```json\n{json.dumps(sessions, indent=2)}\n```")
    else:
        await ctx.send("No active sessions.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    print("Bot is ready!")

# ---------------- Start Flask API in a separate thread ----------------
Thread(target=run_flask, daemon=True).start()

# ---------------- Run Discord bot ----------------
bot.run(DISCORD_BOT_TOKEN)
