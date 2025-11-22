import discord
from discord.ext import commands
from flask import Flask, request, jsonify
from threading import Thread
import uuid
import os
import json
from dotenv import load_dotenv

# ---------------- Load environment variables ----------------
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("API_URL")  # optional, for Discord bot use

# ---------------- Datastore files ----------------
BAN_FILE = "bans.json"
if not os.path.exists(BAN_FILE):
    with open(BAN_FILE, "w") as f:
        json.dump({}, f)

def load_bans():
    with open(BAN_FILE, "r") as f:
        return json.load(f)

def save_bans(bans):
    with open(BAN_FILE, "w") as f:
        json.dump(bans, f, indent=2)

# ---------------- Flask API ----------------
app = Flask(__name__)
sessions = {}

@app.route('/create-session', methods=['POST'])
def create_session():
    data = request.json
    game_id = data.get("game_id")
    player_name = data.get("player_name")

    if not game_id or not player_name:
        return jsonify({"status": "error", "message": "game_id and player_name required"}), 400

    # Check bans
    bans = load_bans()
    if player_name in bans:
        return jsonify({"status": "banned", "reason": bans[player_name]}), 403

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "session_id": session_id,
        "game_id": game_id,
        "player_name": player_name
    }
    return jsonify({"status": "success", "session": sessions[session_id]}), 200

@app.route('/ban-player', methods=['POST'])
def ban_player():
    data = request.json
    player_name = data.get("player_name")
    reason = data.get("reason", "No reason provided")
    if not player_name:
        return jsonify({"status": "error", "message": "player_name required"}), 400

    bans = load_bans()
    bans[player_name] = reason
    save_bans(bans)
    return jsonify({"status": "success", "player_name": player_name, "reason": reason}), 200

@app.route('/unban-player', methods=['POST'])
def unban_player():
    data = request.json
    player_name = data.get("player_name")
    if not player_name:
        return jsonify({"status": "error", "message": "player_name required"}), 400

    bans = load_bans()
    if player_name in bans:
        del bans[player_name]
        save_bans(bans)
        return jsonify({"status": "success", "player_name": player_name}), 200
    return jsonify({"status": "error", "message": "Player not found in bans"}), 404

@app.route('/check-ban/<player_name>', methods=['GET'])
def check_ban(player_name):
    bans = load_bans()
    if player_name in bans:
        return jsonify({"status": "banned", "reason": bans[player_name]}), 200
    return jsonify({"status": "not_banned"}), 200

@app.route('/list-bans', methods=['GET'])
def list_bans():
    bans = load_bans()
    return jsonify(bans), 200

@app.route('/list-sessions', methods=['GET'])
def list_sessions():
    return jsonify(sessions), 200

def run_flask():
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

@bot.command()
async def listbans(ctx):
    bans = load_bans()
    if bans:
        await ctx.send(f"⛔ Banned players: ```json\n{json.dumps(bans, indent=2)}\n```")
    else:
        await ctx.send("No banned players.")

@bot.command()
async def ban(ctx, player_name: str, *, reason: str = "No reason provided"):
    bans = load_bans()
    bans[player_name] = reason
    save_bans(bans)
    await ctx.send(f"✅ {player_name} banned for reason: {reason}")

@bot.command()
async def unban(ctx, player_name: str):
    bans = load_bans()
    if player_name in bans:
        del bans[player_name]
        save_bans(bans)
        await ctx.send(f"✅ {player_name} unbanned")
    else:
        await ctx.send(f"❌ {player_name} is not banned")

@bot.command()
async def checkban(ctx, player_name: str):
    bans = load_bans()
    if player_name in bans:
        await ctx.send(f"⛔ {player_name} is banned: {bans[player_name]}")
    else:
        await ctx.send(f"✅ {player_name} is not banned")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    print("Bot is ready!")

# ---------------- Start Flask API in a thread ----------------
Thread(target=run_flask, daemon=True).start()

# ---------------- Run Discord Bot ----------------
bot.run(DISCORD_BOT_TOKEN)
