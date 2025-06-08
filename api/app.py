from flask import Flask, jsonify, current_app, render_template # Added render_template

# Assuming api/app.py is in the 'api/' directory, and templates are in 'dashboard/templates/'
# The path '../dashboard/templates' should correctly point to the templates directory
# relative to the 'api' directory where app.py resides.
app = Flask(__name__, template_folder='../dashboard/templates')

@app.route("/")
def index():
    """
    Serves the main dashboard page (index.html).
    The dashboard will then use JavaScript to fetch data from the /status endpoint.
    """
    return render_template("index.html")

@app.route("/status")
def status():
    """
    Provides the current operational status of the TikTok bot.
    Accesses shared status information populated by the bot thread.
    """
    # Access shared_status and lock from app.config, set by main.py's run_flask
    shared_status_dict = current_app.config.get('BOT_SHARED_STATUS')
    lock = current_app.config.get('BOT_STATUS_LOCK')

    if shared_status_dict is None or lock is None:
        # This case occurs if the Flask app is run directly via "python api/app.py"
        # or if main.py did not correctly configure the app.
        # It's also a safeguard against accessing None.
        return jsonify({
            "error": "Shared status not configured or not available.",
            "dashboard_service_status": "running_standalone_limited"
        }), 500

    with lock:
        # Create a copy of the shared status to ensure thread safety during access
        # and to prevent modification of the original dict by this thread.
        status_copy = dict(shared_status_dict)

    # Add any other relevant app status if needed
    status_copy["dashboard_service_status"] = "running_with_bot_integration"
    return jsonify(status_copy)

if __name__ == "__main__":
    # This block allows running the Flask app directly for development or testing API endpoints
    # without the bot. Shared status will not be available in this mode.
    app.config['BOT_SHARED_STATUS'] = {
        "status": "dashboard_dev_mode",
        "current_user": "N/A",
        "actions_this_session": -1,
        "last_error": "Running in direct Flask mode, bot status not available."
    }
    # No lock needed for this dummy status in single-threaded dev mode for Flask directly.
    # Or, could assign a dummy lock: from threading import Lock; app.config['BOT_STATUS_LOCK'] = Lock()
    # but it's not strictly necessary if only one thread (Flask dev server) accesses this dummy data.
    app.config['BOT_STATUS_LOCK'] = None # Explicitly set to None if not using a real lock here

    print("Flask app running directly in development mode (no bot integration or full logger).")
    print("API /status will show dummy data.")
    app.run(host='0.0.0.0', port=5000, debug=True)