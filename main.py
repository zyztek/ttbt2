import os
import argparse
from core.bot import TikTokBot
from threading import Thread
from api.app import app

def parse_args():
    parser = argparse.ArgumentParser(description="TikTok Growth Bot")
    parser.add_argument("--mode", choices=["safe", "balanced", "aggressive"], default="safe")
    parser.add_argument("--max-views", type=int, default=50)
    return parser.parse_args()

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    args = parse_args()
    
    os.environ["MAX_VIEWS_PER_HOUR"] = str(args.max_views)

    # Start Flask app in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    bot = TikTokBot()
    try:
        print(f"Iniciando en modo {args.mode}...")
        bot.run_session()
    except Exception as e:
        print(f"Error crítico: {str(e)}")
    finally:
        bot.driver.quit()
        print("Sesión finalizada. Revisar logs para detalles.")