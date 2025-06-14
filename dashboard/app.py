from flask import Flask, render_template, jsonify
import os

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    # Simulates bot status. You may want to integrate your status-checking system here.
    return jsonify({"bots": [
        {"name": "bot1", "status": "ok"},
        {"name": "bot2", "status": "running"}
    ]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))