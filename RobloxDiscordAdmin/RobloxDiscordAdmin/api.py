from flask import Flask, request, jsonify

app = Flask(__name__)

# Store sessions in a dictionary (just for example purposes)
sessions = {}


# Endpoint to start a session
@app.route('/start-session', methods=['POST'])
def start_session():
    session_data = request.json  # Get JSON data from the request body
    session_id = session_data.get('session_id')

    if session_id:
        sessions[session_id] = session_data  # Store session data
        return jsonify({"status": "success", "message": f"Session {session_id} started."}), 200
    return jsonify({"status": "error", "message": "Session ID is required."}), 400


# Endpoint to stop a session
@app.route('/stop-session', methods=['POST'])
def stop_session():
    session_data = request.json
    session_id = session_data.get('session_id')

    if session_id in sessions:
        del sessions[session_id]  # Delete session data
        return jsonify({"status": "success", "message": f"Session {session_id} stopped."}), 200
    return jsonify({"status": "error", "message": "Session not found."}), 404


# Endpoint to get session info
@app.route('/get-session/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id in sessions:
        return jsonify(sessions[session_id]), 200
    return jsonify({"status": "error", "message": "Session not found."}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # This runs the server on localhost:5000
