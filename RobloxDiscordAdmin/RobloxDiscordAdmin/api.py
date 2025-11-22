// index.js
const express = require('express');
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');

const app = express();

// Middleware to parse JSON
app.use(bodyParser.json());

// In-memory session storage
const sessions = {};

// Start session
app.post('/start-session', (req, res) => {
    const { session_name } = req.body;

    if (!session_name) {
        return res.status(400).json({ status: "error", message: "Session name required" });
    }

    const session_id = uuidv4();
    sessions[session_id] = { session_id, session_name };

    return res.status(200).json({ status: "success", session: sessions[session_id] });
});

// Stop session
app.post('/stop-session', (req, res) => {
    const { session_id } = req.body;

    if (sessions[session_id]) {
        delete sessions[session_id];
        return res.status(200).json({ status: "success", message: `Session ${session_id} stopped` });
    }

    return res.status(404).json({ status: "error", message: "Session not found" });
});

// Get session by ID
app.get('/get-session/:session_id', (req, res) => {
    const { session_id } = req.params;

    if (sessions[session_id]) {
        return res.status(200).json(sessions[session_id]);
    }

    return res.status(404).json({ status: "error", message: "Session not found" });
});

// List all sessions
app.get('/list-sessions', (req, res) => {
    return res.status(200).json(sessions);
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
