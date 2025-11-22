from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# In-memory session storage
sessions = {}

@app.route('/start-session', methods=['POST'])
def start_session():
    data = request.json
    session_name = data.get("session_name")

    if not session_name:
        return jsonify({"status": "error", "message": "Session name required"}), 400

    session_id = str(uuid.uuid4())
    sessions[session_id] = {"session_id": session_id, "session_name": session_name}

    return jsonify({"status": "success", "session": sessions[session_id]}), 200

@app.route('/stop-session', methods=['POST'])
def stop_session():
    data = request.json
    session_id = data.get("session_id")

    if session_id in sessions:
        del sessions[session_id]
        return jsonify({"status": "success", "message": f"Session {session_id} stopped"}), 200

    return jsonify({"status": "error", "message": "Session not found"}), 404

@app.route('/get-session/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id in sessions:
        return jsonify(sessions[session_id]), 200
    return jsonify({"status": "error", "message": "Session not found"}), 404

# Optional: list all sessions for debugging
@app.route('/list-sessions', methods=['GET'])
def list_sessions():
    return jsonify(sessions), 200

if __name__ == "__main__":
    # Render sets PORT automatically via environment variable
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
