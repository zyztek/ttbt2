import json
import os
from selenium.webdriver.common.by import By # Added
from core.logger import get_logger # Added

# Initialize logger for this module
config_loader_logger = get_logger(__name__) # Using __name__ for module-level logger

# Mapping from string representations to Selenium By objects
BY_MAPPING = {
    "id": By.ID,
    "name": By.NAME,
    "xpath": By.XPATH,
    "css": By.CSS_SELECTOR, # Common abbreviation for CSS_SELECTOR
    "css_selector": By.CSS_SELECTOR,
    "class_name": By.CLASS_NAME,
    "link_text": By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
    "tag_name": By.TAG_NAME
}

class ConfigLoader:
    """
    A utility class for loading configurations from files.
    Currently supports loading JSON files.
    """
    @staticmethod
    def load(filepath):
        """
        Loads data from a JSON file.

        Args:
            filepath (str): The path to the JSON file.

        Returns:
            dict: The data loaded from the JSON file, or an empty dictionary
                  if the file is not found, not a JSON file, or an error occurs.
        """
        if not os.path.exists(filepath):
            config_loader_logger.error(f"Configuration file not found: {filepath}")
            return {}
        if filepath.endswith(".json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f: # Added encoding
                    return json.load(f)
            except json.JSONDecodeError as e:
                config_loader_logger.error(f"Error decoding JSON from {filepath}: {e}")
                return {}
            except Exception as e:
                config_loader_logger.error(f"An unexpected error occurred while loading {filepath}: {e}")
                return {}
        else:
            config_loader_logger.warning(f"File type not supported for loading: {filepath}. Only .json is supported.")
            return {}
        # Add YAML or other loaders as needed in the future

    @staticmethod
    def load_selectors(filepath="selectors.json"):
        """
        Loads and processes Selenium selectors from a JSON file.

        The JSON file is expected to have a structure where keys are page names
        (or component groups), and values are dictionaries of selectors. Each
        selector is defined by a name and a dictionary containing 'by' (the
        selector strategy, e.g., "xpath", "id") and 'value' (the selector string).

        Example JSON structure:
        {
            "login_page": {
                "username_field": {"by": "id", "value": "user-name"},
                "password_field": {"by": "name", "value": "password"}
            },
            "home_page": {
                "title_header": {"by": "xpath", "value": "//span[@class='title']"}
            }
        }

        Args:
            filepath (str, optional): The path to the JSON file containing
                                      selector definitions. Defaults to "selectors.json".

        Returns:
            dict: A dictionary containing the processed selectors. The structure mirrors
                  the input JSON, but the selector definitions are replaced by tuples
                  of (ByObject, value_string). For example:
                  {
                      "login_page": {
                          "username_field": (By.ID, "user-name"),
                          "password_field": (By.NAME, "password")
                      },
                      ...
                  }
                  Returns an empty dictionary if the file cannot be loaded or is empty,
                  or if there are issues with the selector data format.

        The `BY_MAPPING` constant in this module defines the valid strings for 'by'
        (e.g., "id", "xpath") and their corresponding `selenium.webdriver.common.by.By` objects.
        """
        config_loader_logger.info(f"Loading selectors from: {filepath}")
        raw_data = ConfigLoader.load(filepath)

        if not raw_data: # Handles None or empty dict from load()
            config_loader_logger.warning(f"No data loaded from selector file: {filepath}. Returning empty selectors.")
            return {}

        processed_selectors = {}
        for page_name, page_selectors in raw_data.items():
            if not isinstance(page_selectors, dict):
                config_loader_logger.warning(f"Skipping page '{page_name}' in '{filepath}': expected a dictionary of selectors, got {type(page_selectors)}.")
                continue

            processed_page_selectors = {}
            for selector_name, selector_data in page_selectors.items():
                if not isinstance(selector_data, dict):
                    config_loader_logger.warning(f"Skipping selector '{selector_name}' on page '{page_name}' in '{filepath}': expected a dictionary, got {type(selector_data)}.")
                    continue

                by_string = selector_data.get('by')
                value_string = selector_data.get('value')

                if not by_string or not value_string:
                    config_loader_logger.warning(
                        f"Skipping selector '{selector_name}' on page '{page_name}' in '{filepath}': "
                        f"'by' ({by_string}) or 'value' ({value_string}) is missing or empty."
                    )
                    continue

                by_object = BY_MAPPING.get(by_string.lower())
                if by_object is None:
                    config_loader_logger.warning(
                        f"Skipping selector '{selector_name}' on page '{page_name}' in '{filepath}': "
                        f"Invalid 'by' strategy '{by_string}'. Valid strategies are: {list(BY_MAPPING.keys())}"
                    )
                    continue

                processed_page_selectors[selector_name] = (by_object, value_string)

            if processed_page_selectors: # Only add page if it has valid selectors
                 processed_selectors[page_name] = processed_page_selectors

        if not processed_selectors:
            config_loader_logger.warning(f"No valid selectors processed from file: {filepath}. Raw data was: {raw_data if len(str(raw_data)) < 200 else str(raw_data)[:200] + '...'}")
        else:
            config_loader_logger.info(f"Successfully processed {sum(len(ps) for ps in processed_selectors.values())} selectors from {len(processed_selectors)} pages in '{filepath}'.")

        return processed_selectors