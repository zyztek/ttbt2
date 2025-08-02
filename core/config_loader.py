"""
Módulo de utilidad para cargar configuraciones desde archivos JSON o YAML.
"""
import json
import os
import yaml
from selenium.webdriver.common.by import By
from core.logger import get_logger

logger = get_logger("core.config_loader")

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

class ConfigLoader:
    """
    Configuration loader class that provides static methods for loading configuration files.
    """
    
    @staticmethod
    def load(path):
        """
        Loads configuration data from a JSON or YAML file.
        
        Args:
            path (str): Path to the configuration file.
            
        Returns:
            dict: Dictionary with loaded data. Returns empty dict if file type not supported,
                  file not found, or parsing error occurs.
        """
        if not os.path.exists(path):
            logger.error(f"Configuration file not found: {path}")
            return {}
            
        if path.endswith(".json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {path}: {e}")
                return {}
        elif path.endswith((".yml", ".yaml")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.error(f"Error parsing YAML from {path}: {e}")
                return {}
        else:
            logger.error(f"File type not supported for loading: {path}")
            return {}
            
    @staticmethod
    def load_selectors(path):
        """
        Loads web element selectors from a JSON or YAML file and converts them
        to Selenium By objects.
        
        Args:
            path (str): Path to the selectors configuration file.
            
        Returns:
            dict: Nested dictionary where each page contains selectors as (By, value) tuples.
                  Format: {"page_name": {"element_name": (By.METHOD, "selector_value")}}
        """
        # Mapping from string to Selenium By constants
        BY_MAPPING = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css_selector": By.CSS_SELECTOR,
            "class_name": By.CLASS_NAME,
            "tag_name": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT
        }
        
        raw_data = ConfigLoader.load(path)
        
        if not raw_data:
            logger.warning(f"No data loaded from selector file: {path}")
            return {}
            
        processed_selectors = {}
        
        for page_name, page_data in raw_data.items():
            if not isinstance(page_data, dict):
                logger.warning(f"Skipping page '{page_name}': expected a dictionary of selectors, got {type(page_data)}")
                continue
                
            processed_page_selectors = {}
            
            for selector_name, selector_data in page_data.items():
                if not isinstance(selector_data, dict):
                    logger.warning(f"Skipping selector '{selector_name}' on page '{page_name}': expected a dictionary, got {type(selector_data)}")
                    continue
                    
                by_string = selector_data.get("by")
                value_string = selector_data.get("value")
                
                if not by_string or not value_string:
                    logger.warning(f"Skipping selector '{selector_name}' on page '{page_name}': 'by' ({by_string}) or 'value' ({value_string}) is missing or empty")
                    continue
                    
                by_method = BY_MAPPING.get(by_string.lower())
                if not by_method:
                    logger.warning(f"Invalid 'by' strategy '{by_string}' for selector '{selector_name}' on page '{page_name}'. Skipping.")
                    continue
                    
                processed_page_selectors[selector_name] = (by_method, value_string)
                
            # Only add the page if it has valid selectors
            if processed_page_selectors:
                processed_selectors[page_name] = processed_page_selectors
                
        return processed_selectors
