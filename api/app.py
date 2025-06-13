import os # Added import
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
    # Changed to use FLASK_HOST environment variable, default to 127.0.0.1
    app.run(host=os.environ.get('FLASK_HOST', '127.0.0.1'), port=5000)