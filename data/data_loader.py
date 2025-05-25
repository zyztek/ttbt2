# Loader genérico para datos en formato JSON o YAML
# Todos los comentarios están en español.

import json
import yaml

class DataLoader:
    def __init__(self, data_file):
        """
        Inicializa el DataLoader e intenta cargar los datos.
        :param data_file: Ruta al archivo de datos.
        """
        self.data = self.load_data(data_file)

    def load_data(self, data_file):
        """
        Carga los datos del archivo según su extensión.
        :param data_file: Ruta al archivo.
        :return: Diccionario con los datos o {}.
        """
        if data_file.endswith('.json'):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {}
        elif data_file.endswith(('.yml', '.yaml')):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except (FileNotFoundError, yaml.YAMLError):
                return {}
        return {}