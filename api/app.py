from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"status": "TikTok Bot API running"})

@app.route("/status")
def status():
    # Add any status checks or data gathering here
    return jsonify({
        "bots_running": 3,  # Example static value, replace with actual logic
        "active_users": [],  # Placeholder for active users
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Use port 5000 for development