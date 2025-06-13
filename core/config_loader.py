"""
Módulo de utilidad para cargar configuraciones desde archivos JSON o YAML.
"""
import json
import os # Still needed for os.path.exists if it were used here, but not currently. Retained for now.
import yaml

def load_config(path):
    """
    Carga datos de configuración desde un archivo JSON o YAML.

    Args:
        path (str): La ruta al archivo de configuración.

    Returns:
        dict: Un diccionario con los datos cargados. Retorna un diccionario vacío
              si el tipo de archivo no es soportado, el archivo no se encuentra (implícito),
              o si hay un error de parsing (para YAML). JSON parsing errors might still raise.
    """
    if path.endswith(".json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): # Added FileNotFoundError
            return {}
    elif path.endswith((".yml", ".yaml")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError): # Added FileNotFoundError
            # Handle YAML parsing errors, perhaps log and return empty dict
            return {} # Or raise an exception
    # Fallback for unrecognized file types or if path is None/empty
    return {}
