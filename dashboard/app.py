"""
Módulo de la aplicación Dashboard para el TikTok Bot.

Define una aplicación Flask que sirve una interfaz web simple (dashboard)
para monitorear la actividad y el estado de los bots. Incluye rutas para
renderizar la página principal del dashboard y para obtener datos de estado
en formato JSON, que podrían ser consumidos por el frontend del dashboard.
"""
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    """
    Ruta principal del dashboard.

    Renderiza y sirve la plantilla `index.html`, que constituye la interfaz
    principal del dashboard web.

    Returns:
        str: El contenido HTML renderizado de `index.html`.
    """
    return render_template("index.html")

@app.route("/status")
def status():
    """
    Endpoint API para obtener el estado de los bots.

    Retorna un objeto JSON que contiene información sobre el estado actual
    de los bots (ej. nombres, estados). Esta ruta está diseñada para ser
    utilizada, por ejemplo, por peticiones AJAX desde el frontend del dashboard
    para actualizar dinámicamente la información mostrada.
    Actualmente, los datos son estáticos y sirven como ejemplo.

    Returns:
        Response: Un objeto de respuesta Flask con contenido JSON.
                  Ej: {"bots": [{"name": "bot1", "status": "ok"}, ...]}
    """
    # Simulates bot status. You may want to integrate your status-checking system here.
    return jsonify({"bots": [
        {"name": "bot1", "status": "ok"},
        {"name": "bot2", "status": "running"}
    ]})

if __name__ == "__main__":
    # Changed to use FLASK_HOST environment variable, default to 127.0.0.1
    app.run(host=os.environ.get('FLASK_HOST', '127.0.0.1'), port=int(os.environ.get("PORT", 5000)))