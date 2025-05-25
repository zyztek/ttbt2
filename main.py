import os
import argparse
import logging
from core.bot import TikTokBot
from config.retry import retry

# Set up logging
logging.basicConfig(level=logging.INFO)

def parse_args():
    parser = argparse.ArgumentParser(description="TikTok Growth Bot")
    parser.add_argument("--mode", choices=["safe", "balanced", "aggressive"], default="safe")
    parser.add_argument("--max-views", type=int, default=50)
    return parser.parse_args()

def run_bot():
    args = parse_args()
    os.environ["MAX_VIEWS_PER_HOUR"] = str(args.max_views)

    bot = TikTokBot()
    try:
        logging.info(f"Starting in {args.mode} mode...")
        retry(bot.run_session)
    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
    finally:
        bot.driver.quit()
        logging.info("Session ended. Check logs for details.")

if __name__ == "__main__":
    run_bot()