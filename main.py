"""
Punto de entrada principal para el TikTok Bot.

Este script inicializa y ejecuta una sesión del TikTokBot, configurando su
comportamiento a través de argumentos de línea de comandos. También inicia un
servidor Flask en un hilo separado para exponer una API (definida en api.app).
"""
import os
import sys
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
    """
    Inicia el servidor de desarrollo Flask para la API.

    El host es configurable mediante la variable de entorno FLASK_HOST,
    con '127.0.0.1' como valor predeterminado. El puerto está fijado en 5000.
    """
    # Changed to use FLASK_HOST environment variable, default to 127.0.0.1
    app.run(host=os.environ.get('FLASK_HOST', '127.0.0.1'), port=5000)

def main_script_logic(args):
    """
    Orquesta la lógica principal del bot y el inicio del servidor API.

    Utiliza los argumentos parseados para configurar el entorno del bot (ej. MAX_VIEWS_PER_HOUR),
    luego inicializa una instancia de TikTokBot y ejecuta su sesión. Maneja la inicialización
    y limpieza del driver del bot. Finalmente, inicia el servidor Flask API en un hilo separado.

    Args:
        args (argparse.Namespace): Objeto con los argumentos parseados de la línea de comandos,
                                   esperado tener atributos como `mode` y `max_views`.
    """
    # Pass max views as environment variable
    os.environ["MAX_VIEWS_PER_HOUR"] = str(args.max_views)
    bot = None # Initialize bot to None for broader scope

    try:
        print(f"Iniciando en modo {args.mode}...")
        # Single bot initialization
        bot = TikTokBot()
        if not bot.driver:
            print("Failed to initialize bot - Chrome driver not available")
            # Consider using sys.exit(1) for clearer exit status
            sys.exit(1) # Changed to sys.exit(1)
        bot.run_session()
    except Exception as e:
        print(f"Error crítico: {str(e)}")
    finally:
        if bot and hasattr(bot, 'driver') and bot.driver: # Check hasattr for driver
            try:
                bot.driver.quit()
            except Exception as cleanup_error:
                print(f"Error closing driver: {cleanup_error}")
        # Clarify end of bot session
        print("Sesión de bot principal finalizada.")

    # Start Flask app after bot session
    print("Iniciando servidor Flask...")
    flask_thread = Thread(target=run_flask)
    # flask_thread.daemon = True # Optional: make it a daemon thread
    flask_thread.start()
    # print("Servidor Flask iniciado en un hilo separado.") # Optional

if __name__ == "__main__":
    parsed_args = parse_args()
    main_script_logic(parsed_args)