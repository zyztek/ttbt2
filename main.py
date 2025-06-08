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
from core.bot import TikTokBot
from threading import Thread
from api.app import app # Flask app for the dashboard
from core.logger import get_logger
from selenium.common.exceptions import WebDriverException

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
        default="balanced",
        help="Operational mode for the bot (default: balanced)."
    )
    parser.add_argument(
        "--max-views",
        type=int,
        default=5000,
        help="Maximum number of views to attempt in a session (default: 5000)."
    )
    return parser.parse_args()

def run_flask():
    """
    Starts the Flask web server for the bot's dashboard.

    The server runs on host 0.0.0.0 and port 5000.
    This function is intended to be run in a separate thread to avoid blocking
    the main bot operations.
    """
    # Note: Flask's development server is not recommended for production.
    # For production, a more robust WSGI server (e.g., Gunicorn, uWSGI) should be used.
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()
    logger.info(f"Application started with arguments: mode={args.mode}, max_views={args.max_views}")
    
    # Set environment variable for max views, accessible by other modules
    os.environ["MAX_VIEWS_PER_HOUR"] = str(args.max_views)
    logger.debug(f"MAX_VIEWS_PER_HOUR environment variable set to: {args.max_views}")

    # Initialize and start the Flask dashboard in a separate thread
    logger.info("Initializing and starting Flask dashboard thread.")
    flask_thread = Thread(target=run_flask, daemon=True) # Set as daemon to exit with main thread
    flask_thread.start()

    bot = None  # Initialize bot variable to ensure it's available in finally block
    try:
        # Initialize the TikTokBot
        logger.info(f"Initializing TikTokBot in mode: {args.mode}...")
        bot = TikTokBot(mode=args.mode)

        # Check if WebDriver was initialized successfully
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