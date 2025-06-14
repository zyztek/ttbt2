# Fingerprint manager for the TTBT1 framework.
# Allows random selection of fingerprints.
# Loads fingerprints from a JSON file by default.

import random
from core.config_loader import ConfigLoader # Added
from core.logger import get_logger # Added

# Initialize logger for this module
fingerprint_manager_logger = get_logger(__name__)

class FingerprintManager:
    """
    Manages a list of browser fingerprints.
    Fingerprints can be provided directly or loaded from a specified JSON file.

    Attributes:
        fingerprints (list): A list of fingerprint strings.
    """
    def __init__(self, fingerprints=None, filepath="fingerprints/fingerprints.json"):
        """
        Initializes the FingerprintManager.

        If a list of fingerprints is provided directly, it's used. Otherwise,
        fingerprints are loaded from the specified JSON file.

        Args:
            fingerprints (list, optional): A list of fingerprint strings. Defaults to None.
            filepath (str, optional): Path to the JSON file containing fingerprints.
                                      Defaults to "fingerprints/fingerprints.json".
                                      Expected format: {"fingerprints": ["fp1", "fp2", ...]}
        """
        loaded_fingerprints_list = []
        if fingerprints is None:
            fingerprint_manager_logger.info(f"No direct fingerprints provided, attempting to load from '{filepath}'.")
            raw_data = ConfigLoader.load(filepath)
            if isinstance(raw_data, dict) and "fingerprints" in raw_data and isinstance(raw_data["fingerprints"], list):
                loaded_fingerprints_list = raw_data["fingerprints"]
                fingerprint_manager_logger.info(f"Successfully loaded {len(loaded_fingerprints_list)} fingerprints from '{filepath}'.")
            else:
                fingerprint_manager_logger.warning(
                    f"Failed to load fingerprints from '{filepath}' or data is not in expected format "
                    f"(e.g., {{'fingerprints': [...]}}). Found: {type(raw_data)}. Initializing with empty fingerprint list."
                )
                loaded_fingerprints_list = []
        else:
            fingerprint_manager_logger.info(f"Using {len(fingerprints)} directly provided fingerprints.")
            loaded_fingerprints_list = fingerprints

        self.fingerprints = loaded_fingerprints_list

    def get_fingerprint(self):
        """
        Returns a random fingerprint from the list.

        Returns:
            str or None: A randomly selected fingerprint string, or None if no
                         fingerprints are available.
        """
        if not self.fingerprints:
            fingerprint_manager_logger.warning("get_fingerprint called, but no fingerprints available.")
            return None
        selected_fingerprint = random.choice(self.fingerprints)
        fingerprint_manager_logger.debug(f"Selected fingerprint: {selected_fingerprint[:70]}...") # Log a snippet
        return selected_fingerprint