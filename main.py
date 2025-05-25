import os
import argparse
from core.bot import TikTokBot
from threading import Thread
from api.app import app

def parse_args():
    parser = argparse.ArgumentParser(description="TikTok Bot")
    parser.add_argument("--mode", choices=["safe", "balanced", "aggressive"], default="balanced")
    parser.add_argument("--max-views", type=int, default=5000)
    return parser.parse_args()

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    args = parse_args()
    
# Pass max views as environment variable
    os.environ["MAX_VIEWS_PER_HOUR"] = str(args.max_views)
    bot = None
    try:
        print(f"Iniciando en modo {args.mode}...")
        bot = TikTokBot()
        if not bot.driver:
            print("Failed to initialize bot - Chrome driver not available")
            exit(1)
        bot.run_session()
    except Exception as e:
        print(f"Error crítico: {str(e)}")
    finally:
        if bot and bot.driver:
            try:
                bot.driver.quit()
            except Exception as cleanup_error:
                print(f"Error closing driver: {cleanup_error}")
        print("Sesión finalizada. Revisar logs para detalles.")


    os.environ["MAX_VIEWS_PER_HOUR"] = str(args.max_views)

    # Start Flask app in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    bot = TikTokBot()
    
  