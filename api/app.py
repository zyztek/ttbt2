"""
Módulo API para el TikTok Bot.

Define una aplicación Flask que expone endpoints para monitorear y potencialmente
controlar la actividad del bot. Actualmente, proporciona un endpoint de estado
básico y una ruta índice.
"""
import os
from flask import Flask, jsonify, render_template

# Assuming api/app.py is in the 'api/' directory, and templates are in 'dashboard/templates/'
# The path '../dashboard/templates' should correctly point to the templates directory
# relative to the 'api' directory where app.py resides.
app = Flask(__name__, template_folder='../dashboard/templates')

@app.route("/")
def index():
    """
    Returns the API status in JSON format.
    """
    return jsonify({"status": "TikTok Bot API running"})

@app.route("/status")
def status():
    """
    Ruta de estado de la API.

    Retorna un objeto JSON con información sobre el estado actual del bot o bots.
    Actualmente, los datos son estáticos y sirven como ejemplo. En una implementación
    completa, estos datos se obtendrían dinámicamente del sistema del bot.

    Returns:
        Response: Un objeto de respuesta Flask con contenido JSON.
                  Ej: {"bots_running": 3, "active_users": []}
    """
    # Add any status checks or data gathering here
    return jsonify({
        "bots_running": 3,  # Example static value, replace with actual logic
        "active_users": [],  # Placeholder for active users
    })

if __name__ == "__main__":
    # Changed to use FLASK_HOST environment variable, default to 127.0.0.1
    app.run(host=os.environ.get('FLASK_HOST', '127.0.0.1'), port=5000)
