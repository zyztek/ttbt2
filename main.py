import os
import argparse
from core.bot import TikTokBot

def parse_args():
    parser = argparse.ArgumentParser(description="TikTok Growth Bot")
    parser.add_argument("--mode", choices=["safe", "balanced", "aggressive"], default="safe")
    parser.add_argument("--max-views", type=int, default=50)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Pass max views as env var so the bot can find it (or refactor bot to accept it as arg)
    os.environ["MAX_VIEWS_PER_HOUR"] = str(args.max_views)

    bot = TikTokBot()
    try:
        print(f"Iniciando en modo {args.mode}...")
        bot.run_session()
    except Exception as e:
        print(f"Error crítico: {str(e)}")
    finally:
        bot.driver.quit()
        print("Sesión finalizada. Revisar logs para detalles.")