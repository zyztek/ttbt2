"""
Módulo de utilidad para la carga de datos desde archivos JSON o YAML.

Proporciona una clase DataLoader que simplifica el proceso de leer
datos estructurados desde el sistema de archivos, manejando diferentes
formatos y errores comunes de lectura o parseo.
"""
# Loader genérico para datos en formato JSON o YAML
# Todos los comentarios están en español.

import json
import yaml

class DataLoader:
    """
    Clase para cargar y mantener datos desde un archivo JSON o YAML especificado.

    Al instanciar, intenta cargar los datos desde la ruta de archivo proporcionada.
    Los datos cargados se almacenan en el atributo `self.data`.
    """
    def __init__(self, data_file):
        """
        Inicializa el DataLoader e intenta cargar los datos desde el archivo.

        Args:
            data_file (str): La ruta al archivo de datos (JSON o YAML)
                             desde donde se cargarán los datos.
        """
        self.data = self.load_data(data_file)

    def load_data(self, path): # Changed argument name to 'path' for clarity in new docstring
        """
        Carga los datos del archivo especificado por `path` según su extensión.

        Maneja archivos con extensión '.json', '.yml', o '.yaml'.
        Si el archivo no se encuentra, no se puede parsear (JSONDecodeError para JSON,
        YAMLError para YAML), o tiene una extensión no reconocida, retorna un
        diccionario vacío.

        Args:
            path (str): La ruta al archivo de datos.

        Returns:
            dict: Un diccionario con los datos cargados desde el archivo.
                  Retorna un diccionario vacío en caso de error o tipo de archivo no soportado.
        """
        if path.endswith('.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f: # Corrected data_file to path
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {}
        elif path.endswith(('.yml', '.yaml')):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except (FileNotFoundError, yaml.YAMLError):
                return {}
        return {}