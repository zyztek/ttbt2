# Proxy manager for the TTBT1 framework.
# Allows selection and deactivation of proxies.
# Loads proxies from a JSON file by default.

import random
from core.config_loader import ConfigLoader # Added
from core.logger import get_logger # Added

# Initialize logger for this module
proxy_manager_logger = get_logger(__name__)

class ProxyManager:
    """
    Manages a list of proxies, allowing for random selection and deactivation.
    Proxies can be provided directly or loaded from a specified JSON file.

    Attributes:
        proxies (list): The initial list of all proxies.
        active_proxies (set): A set of proxies currently considered active and usable.
    """
    def __init__(self, proxies=None, filepath="proxies/proxies.json"):
        """
        Initializes the ProxyManager.

        If a list of proxies is provided directly, it's used. Otherwise,
        proxies are loaded from the specified JSON file.

        Args:
            proxies (list, optional): A list of proxy strings. Defaults to None.
            filepath (str, optional): Path to the JSON file containing proxies.
                                      Defaults to "proxies/proxies.json".
                                      Expected format: {"proxies": ["http://...", ...]}
        """
        loaded_proxies_list = []
        if proxies is None:
            proxy_manager_logger.info(f"No direct proxies provided, attempting to load from '{filepath}'.")
            raw_data = ConfigLoader.load(filepath)
            if isinstance(raw_data, dict) and "proxies" in raw_data and isinstance(raw_data["proxies"], list):
                loaded_proxies_list = raw_data["proxies"]
                proxy_manager_logger.info(f"Successfully loaded {len(loaded_proxies_list)} proxies from '{filepath}'.")
            else:
                proxy_manager_logger.warning(
                    f"Failed to load proxies from '{filepath}' or data is not in expected format "
                    f"(e.g., {{'proxies': [...]}}). Found: {type(raw_data)}. Initializing with empty proxy list."
                )
                loaded_proxies_list = []
        else:
            proxy_manager_logger.info(f"Using {len(proxies)} directly provided proxies.")
            loaded_proxies_list = proxies

        self.proxies = loaded_proxies_list
        self.active_proxies = set(self.proxies) # Initialize active_proxies with all loaded/provided proxies

    def get_random_active_proxy(self):
        """
        Returns a random active proxy.

        Returns:
            str or None: A randomly selected proxy string from the active set,
                         or None if no active proxies are available.
        """
        if not self.active_proxies:
            proxy_manager_logger.warning("get_random_active_proxy called, but no active proxies available.")
            return None
        selected_proxy = random.choice(list(self.active_proxies))
        proxy_manager_logger.debug(f"Selected active proxy: {selected_proxy}")
        return selected_proxy

    def deactivate_proxy(self, proxy):
        """
        Deactivates a proxy by removing it from the set of active proxies.

        This is typically used if a proxy is found to be blocked or unresponsive.

        Args:
            proxy (str): The proxy string to deactivate.
        """
        if proxy in self.active_proxies:
            self.active_proxies.discard(proxy)
            proxy_manager_logger.info(f"Proxy deactivated: {proxy}. Remaining active proxies: {len(self.active_proxies)}")
        else:
            proxy_manager_logger.warning(f"Attempted to deactivate proxy not in active set: {proxy}")