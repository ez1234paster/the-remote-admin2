// index.js
require('dotenv').config();
const fs = require('fs');
const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { Client, GatewayIntentBits, Partials, REST, Routes, Collection } = require('discord.js');

const app = express();
app.use(express.json()); // parse JSON body

// ---------------- Datastore ----------------
const BAN_FILE = 'bans.json';
if (!fs.existsSync(BAN_FILE)) fs.writeFileSync(BAN_FILE, '{}');

function loadBans() {
    return JSON.parse(fs.readFileSync(BAN_FILE, 'utf8'));
}

function saveBans(bans) {
    fs.writeFileSync(BAN_FILE, JSON.stringify(bans, null, 2));
}

// ---------------- In-memory sessions ----------------
const sessions = {};

// ---------------- Express API ----------------

// Create session
app.post('/create-session', (req, res) => {
    const { game_id, player_name } = req.body;
    if (!game_id || !player_name) return res.status(400).json({ status: 'error', message: 'game_id and player_name required' });

    const bans = loadBans();
    if (bans[player_name]) return res.status(403).json({ status: 'banned', reason: bans[player_name] });

    const session_id = uuidv4();
    sessions[session_id] = { session_id, game_id, player_name };
    res.json({ status: 'success', session: sessions[session_id] });
});

// Ban player
app.post('/ban-player', (req, res) => {
    const { player_name, reason = 'No reason provided' } = req.body;
    if (!player_name) return res.status(400).json({ status: 'error', message: 'player_name required' });

    const bans = loadBans();
    bans[player_name] = reason;
    saveBans(bans);
    res.json({ status: 'success', player_name, reason });
});

// Unban player
app.post('/unban-player', (req, res) => {
    const { player_name } = req.body;
    if (!player_name) return res.status(400).json({ status: 'error', message: 'player_name required' });

    const bans = loadBans();
    if (bans[player_name]) {
        delete bans[player_name];
        saveBans(bans);
        res.json({ status: 'success', player_name });
    } else {
        res.status(404).json({ status: 'error', message: 'Player not found in bans' });
    }
});

// Check ban
app.get('/check-ban/:player_name', (req, res) => {
    const bans = loadBans();
    const { player_name } = req.params;
    if (bans[player_name]) res.json({ status: 'banned', reason: bans[player_name] });
    else res.json({ status: 'not_banned' });
});

// List bans
app.get('/list-bans', (req, res) => res.json(loadBans()));

// List sessions
app.get('/list-sessions', (req, res) => res.json(sessions));

// Start Express server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`API running on port ${PORT}`));

// ---------------- Discord Bot ----------------
const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] });
const BOT_TOKEN = process.env.DISCORD_BOT_TOKEN;

client.once('ready', () => console.log(`Logged in as ${client.user.tag}`));

client.on('messageCreate', async message => {
    if (message.author.bot) return;

    const args = message.content.split(' ');
    const command = args.shift().toLowerCase();

    // ---------------- Commands ----------------
    if (command === '!listsessions') {
        if (Object.keys(sessions).length > 0) {
            message.channel.send(`📄 All sessions: \`\`\`json\n${JSON.stringify(sessions, null, 2)}\n\`\`\``);
        } else message.channel.send('No active sessions.');
    }

    else if (command === '!listbans') {
        const bans = loadBans();
        if (Object.keys(bans).length > 0) {
            message.channel.send(`⛔ Banned players: \`\`\`json\n${JSON.stringify(bans, null, 2)}\n\`\`\``);
        } else message.channel.send('No banned players.');
    }

    else if (command === '!ban') {
        const player_name = args[0];
        const reason = args.slice(1).join(' ') || 'No reason provided';
        if (!player_name) return message.channel.send('❌ Usage: !ban <player_name> [reason]');

        const bans = loadBans();
        bans[player_name] = reason;
        saveBans(bans);
        message.channel.send(`✅ ${player_name} banned for reason: ${reason}`);
    }

    else if (command === '!unban') {
        const player_name = args[0];
        if (!player_name) return message.channel.send('❌ Usage: !unban <player_name>');

        const bans = loadBans();
        if (bans[player_name]) {
            delete bans[player_name];
            saveBans(bans);
            message.channel.send(`✅ ${player_name} unbanned`);
        } else message.channel.send(`❌ ${player_name} is not banned`);
    }

    else if (command === '!checkban') {
        const player_name = args[0];
        if (!player_name) return message.channel.send('❌ Usage: !checkban <player_name>');

        const bans = loadBans();
        if (bans[player_name]) message.channel.send(`⛔ ${player_name} is banned: ${bans[player_name]}`);
        else message.channel.send(`✅ ${player_name} is not banned`);
    }
});

client.login(BOT_TOKEN);
