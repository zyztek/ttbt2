"""
Main entry point for the TikTok Bot application.

This script handles:
- Parsing command-line arguments for bot configuration.
- Setting up environment variables.
- Initializing and starting the Flask web server for the dashboard in a separate thread.
- Initializing the TikTokBot instance.
- Running the bot's session.
- Ensuring graceful shutdown and resource cleanup.
"""
import os
import argparse
import threading # Added
from core.bot import TikTokBot
from threading import Thread
from api.app import app # Flask app for the dashboard
from core.logger import get_logger
from selenium.common.exceptions import WebDriverException
from config.settings import ( # Added
    DEFAULT_BOT_MODE, MAX_VIEWS_DEFAULT_ARG,
    FLASK_HOST, FLASK_PORT
)

# Initialize logger for the main runner
logger = get_logger("main_runner")

def parse_args():
    """
    Defines and parses command-line arguments for the bot.

    Current arguments:
    --mode: Defines the operational mode of the bot (e.g., 'safe', 'balanced', 'aggressive').
    --max-views: Sets the maximum number of views the bot should attempt in a session.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="TikTok Bot")
    parser.add_argument(
        "--mode",
        choices=["safe", "balanced", "aggressive"],
        default=DEFAULT_BOT_MODE, # Used settings constant
        help=f"Operational mode for the bot (default: {DEFAULT_BOT_MODE})."
    )
    parser.add_argument(
        "--max-views",
        type=int,
        default=MAX_VIEWS_DEFAULT_ARG, # Used settings constant
        help=f"Maximum number of views to attempt in a session (default: {MAX_VIEWS_DEFAULT_ARG})."
    )
    return parser.parse_args()

def run_flask(flask_app, shared_status, lock): # Modified signature
    """
    Starts the Flask web server for the bot's dashboard.

    Host and port are sourced from config.settings.
    This function is intended to be run in a separate thread to avoid blocking
    the main bot operations.
    """
    # Note: Flask's development server is not recommended for production.
    # For production, a more robust WSGI server (e.g., Gunicorn, uWSGI) should be used.
    # Pass shared_status and lock to the app context if needed by routes
    # For example, flask_app.config['SHARED_STATUS'] = shared_status
    # flask_app.config['STATUS_LOCK'] = lock
    logger.info(f"Starting Flask server on {FLASK_HOST}:{FLASK_PORT}")
    flask_app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False) # Used settings constants

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()
    logger.info(f"Application started with arguments: mode={args.mode}, max_views={args.max_views}")
    
    # Set environment variable for max views, accessible by other modules
    os.environ["MAX_VIEWS_PER_HOUR"] = str(args.max_views)
    logger.debug(f"MAX_VIEWS_PER_HOUR environment variable set to: {args.max_views}")

    # --- Shared status and lock for inter-thread communication ---
    bot_shared_status = {
        "status": "initializing", # Overall status: initializing, running, error, stopped
        "current_user": None,     # Current TikTok account being used
        "actions_this_session": 0,# Counter for actions in the current run
        "total_actions_lifetime": 0, # Placeholder for persistent stats
        "last_error": None,       # Description of the last critical error
        "mode": args.mode,        # Bot's operational mode, set at startup
        "last_auth_duration": 0.0, # Duration of the last authentication attempt
        "last_action_cycle_duration": 0.0 # Duration of the last full action cycle
    }
    status_lock = threading.Lock()
    logger.info("Shared status dictionary and lock created.")

    # Initialize and start the Flask dashboard in a separate thread
    logger.info("Initializing and starting Flask dashboard thread.")
    # Pass the main Flask app instance (app), shared status, and lock to the thread
    flask_thread = Thread(target=run_flask, args=(app, bot_shared_status, status_lock), daemon=True)
    flask_thread.start()

    bot = None  # Initialize bot variable to ensure it's available in finally block
    try:
        # Initialize the TikTokBot, passing shared status and lock
        logger.info(f"Initializing TikTokBot in mode: {args.mode}...")
        bot = TikTokBot(mode=args.mode, shared_status=bot_shared_status, status_lock=status_lock)

        # Check if WebDriver was initialized successfully
        # The bot's __init__ should update shared_status if WebDriver fails
        if not bot.driver:
            logger.error("Failed to initialize TikTokBot: WebDriver (e.g., Chrome driver) is not available or failed to start.")
            # Consider a more graceful exit or retry mechanism here if appropriate
            exit(1)

        logger.info("TikTokBot initialized successfully, starting main session.")
        bot.run_session() # Execute the bot's main operational loop

    except WebDriverException as wd_e:
        logger.error(f"A WebDriver-related error occurred during bot operation: {wd_e}")
        # This could be due to browser crashing, driver issues, etc.
    except Exception as e:
        # Catch any other unhandled exceptions during bot setup or execution
        logger.exception("An unhandled exception occurred in the main execution block:")
    finally:
        # Cleanup resources
        logger.info("Initiating shutdown and resource cleanup...")
        if bot and bot.driver:
            try:
                logger.info("Attempting to close WebDriver.")
                bot.driver.quit()
                logger.info("WebDriver closed successfully.")
            except WebDriverException as cleanup_wd_error:
                logger.error(f"WebDriver error during cleanup: {cleanup_wd_error}")
            except Exception as cleanup_error:
                logger.error(f"An unexpected error occurred during WebDriver cleanup: {cleanup_error}")
        else:
            logger.info("No active WebDriver to close, or bot was not fully initialized.")

        # Note: The Flask thread is a daemon, so it will exit when the main thread exits.
        # If it weren't a daemon, explicit shutdown might be needed here.
        logger.info("Application session finished. Review logs for details.")