"""
Módulo de evasión de detección centrado en datos (fingerprints y proxies).

Este módulo proporciona la clase `Evasion`, que gestiona la rotación de
identidades de navegador (fingerprints) y direcciones IP (proxies) para
ayudar a los bots a evitar la detección basada en patrones de estos elementos.

Se diferencia de `core.evasion_system`, que se enfoca en modificar
directamente el estado del driver del navegador para ocultar indicadores
de automatización (ej. `navigator.webdriver`).
"""
# Módulo de evasión para el framework TTBT1
# Proporciona utilidades para rotar fingerprints y proxies.
# Todos los comentarios están en español.

import random
from selenium.webdriver.common.by import By
from core.logger import get_logger
from config.settings import BEHAVIOR_PROFILES, DEFAULT_BOT_MODE # Added

# Initialize a logger for this module
logger = get_logger("HumanBehaviorSimulator")

class HumanBehaviorSimulator:
    """
    Simulates human-like behavior for web automation tasks.

    This class provides methods for actions like typing, clicking, scrolling,
    and introducing delays. Behavioral parameters (e.g., delay durations,
    scroll amounts) are loaded from `config.settings.BEHAVIOR_PROFILES`
    based on an operational mode ('safe', 'balanced', 'aggressive').

    Attributes:
        driver: The Selenium WebDriver instance.
        mode (str): The current operational mode.
        # Current behavioral parameters derived from the selected profile:
        current_delay_multiplier (float): General delay multiplier.
        current_typing_delay_min (float): Min delay between keystrokes.
        current_typing_delay_max (float): Max delay between keystrokes.
        current_space_pause_chance (float): Probability of a longer pause after a space.
        current_space_pause_min_duration (float): Min duration for space pause.
        current_space_pause_max_duration (float): Max duration for space pause.
        current_video_watch_min (float): Min video watch time.
        current_video_watch_max (float): Max video watch time.
        current_click_min_delay (float): Min base delay for human_click.
        current_click_max_delay (float): Max base delay for human_click.
        current_scroll_min_pixels (int): Min scroll distance.
        current_scroll_max_pixels (int): Max scroll distance.
        current_scroll_pause_min (float): Min pause after scrolling.
        current_scroll_pause_max (float): Max pause after scrolling.
        LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER (str): Placeholder for a like button selector.
    """
    def __init__(self, driver, mode='balanced'):
        """
        Initializes the HumanBehaviorSimulator.

        Behavioral parameters are loaded from `config.settings.BEHAVIOR_PROFILES`
        based on the provided `mode`.

        Args:
            driver: The Selenium WebDriver instance.
            mode (str, optional): The simulation mode ('safe', 'balanced', 'aggressive').
                                  Defaults to 'balanced'.
        """
        self.driver = driver
        self.mode = mode.lower() # Ensure mode is consistently lowercase
        logger.info(f"HumanBehaviorSimulator initializing with mode: {self.mode}")

        # Fetch the behavior profile for the current mode, or default if mode is invalid
        current_profile = BEHAVIOR_PROFILES.get(self.mode, BEHAVIOR_PROFILES[DEFAULT_BOT_MODE])
        if self.mode not in BEHAVIOR_PROFILES:
            logger.warning(f"Mode '{self.mode}' not found in BEHAVIOR_PROFILES. Using default mode '{DEFAULT_BOT_MODE}'.")
            self.mode = DEFAULT_BOT_MODE # Update mode to default if it was invalid

        logger.debug(f"Loading behavior profile for mode: {self.mode}")

        # Set instance attributes from the loaded profile
        self.current_delay_multiplier = current_profile['delay_multiplier']

        typing_range = current_profile['typing_delay_range_secs']
        self.current_typing_delay_min = typing_range[0]
        self.current_typing_delay_max = typing_range[1]

        self.current_space_pause_chance = current_profile['space_pause_chance']
        space_pause_duration_range = current_profile['space_pause_duration_range_secs']
        self.current_space_pause_min_duration = space_pause_duration_range[0]
        self.current_space_pause_max_duration = space_pause_duration_range[1]

        video_watch_range = current_profile['video_watch_time_range_secs']
        self.current_video_watch_min = video_watch_range[0]
        self.current_video_watch_max = video_watch_range[1]

        click_delay_range = current_profile['click_base_delay_range_secs']
        self.current_click_min_delay = click_delay_range[0]
        self.current_click_max_delay = click_delay_range[1]

        scroll_amount_range = current_profile['scroll_amount_range_pixels']
        self.current_scroll_min_pixels = scroll_amount_range[0]
        self.current_scroll_max_pixels = scroll_amount_range[1]

        scroll_pause_range = current_profile['scroll_pause_duration_range_secs']
        self.current_scroll_pause_min = scroll_pause_range[0]
        self.current_scroll_pause_max = scroll_pause_range[1]

class Evasion:
    """
    Gestiona y rota listas de fingerprints y proxies para un bot.

    Esta clase mantiene colecciones de fingerprints (perfiles de navegador)
    y proxies (direcciones IP). Ofrece métodos para seleccionar aleatoriamente
    un elemento de cada colección y para aplicar estos elementos a una instancia
    de bot dada, asumiendo que el bot tiene métodos `assign_fingerprint` y
    `assign_proxy`.
    """
    def __init__(self, fingerprints, proxies):
        """
        Inicializa la instancia de Evasion con listas de fingerprints y proxies.

        Args:
            fingerprints (list): Una lista de fingerprints (ej. strings o dicts) disponibles.
            proxies (list): Una lista de proxies (ej. strings de 'ip:port') disponibles.
        """
        logger.debug(f"Human_click: Attempting to click element. Mode: '{self.mode}'")
        # Use self.random_delay, which incorporates the mode-specific multiplier.
        # The base delays (current_click_min_delay, current_click_max_delay) are from settings.
        self.random_delay(self.current_click_min_delay, self.current_click_max_delay) # Pre-click delay.
        element.click()
        logger.trace("Human_click: Element clicked.")
        self.random_delay(self.current_click_min_delay, self.current_click_max_delay) # Post-click delay.

    def watch_video(self):
        """
        Simulates watching a video for a duration determined by the current mode.

        The actual watch time is a random value between `self.current_video_watch_min`
        and `self.current_video_watch_max`, further adjusted by `self.current_delay_multiplier`
        via the `random_delay` method.
        """
        # The base duration is defined by current_video_watch_min/max.
        # random_delay will then apply the current_delay_multiplier to this base range.
        logger.debug(f"Simulating watching video (Mode: {self.mode}). Base duration range: {self.current_video_watch_min}-{self.current_video_watch_max}s.")
        self.random_delay(self.current_video_watch_min, self.current_video_watch_max)


    def like_video(self):
        """
        Simulates liking a video by attempting to click a 'like' button.

        Uses a placeholder XPath selector (`self.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER`)
        for the like button. This selector is for demonstration purposes and
        will likely need to be updated for a specific website.
        The click action itself is performed using `self.human_click`.
        """
        logger.debug(f"Attempting to simulate liking a video (Mode: {self.mode}).")
        try:
            # This selector is a placeholder. For a real application, this XPath
            # would need to be specific and robust for the target website's like button.
            logger.debug(f"Attempting to find like button with placeholder XPath: {self.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER}")
            like_button = self.driver.find_element(By.XPATH, self.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER)
            logger.debug(f"Placeholder like button found.")
            self.human_click(like_button)
            logger.info("Placeholder like button clicked successfully.")
        except Exception as e:
            # Log a warning because this is a placeholder action. In a real scenario,
            # failure to find a critical element might be an error.
            logger.warning(f"Could not click placeholder like button (this is expected if selector is not valid for current page): {e}")

    def random_scroll(self):
        """
        Simulates a random scroll action on the page.

        The scroll distance (in pixels) is a random integer between
        `self.current_scroll_min_pixels` and `self.current_scroll_max_pixels`.
        After scrolling, a pause is introduced, determined by
        `self.current_scroll_pause_min` and `self.current_scroll_pause_max`,
        and adjusted by `self.current_delay_multiplier` via `random_delay`.
        """
        scroll_amount = random.randint(self.current_scroll_min_pixels, self.current_scroll_max_pixels)
        logger.debug(f"Simulating random scroll of {scroll_amount} pixels (Mode: {self.mode}). Base pause range: {self.current_scroll_pause_min}-{self.current_scroll_pause_max}s.")

        # Execute JavaScript to scroll the window.
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        logger.trace(f"Scrolled by {scroll_amount} pixels.")

        # Pause after scrolling. The base duration for this pause comes from current_scroll_pause_min/max.
        # random_delay will then apply the current_delay_multiplier.
        self.random_delay(self.current_scroll_pause_min, self.current_scroll_pause_max)
            'safe': 1.5,
            'balanced': 1.0,
            'aggressive': 0.7
        }
        self.typing_delay_ranges = { # (min_char_delay, max_char_delay)
            'safe': (0.1, 0.25),
            'balanced': (0.05, 0.15),
            'aggressive': (0.02, 0.08)
        }
        self.video_watch_time_ranges = { # (min_watch_seconds, max_watch_seconds)
            'safe': (10, 25),
            'balanced': (5, 15),
            'aggressive': (3, 8)
        }
        self.scroll_amount_ranges = { # (min_pixels, max_pixels)
            'safe': (200, 500),
            'balanced': (300, 700),
            'aggressive': (500, 1000)
        }
        self.scroll_pause_ranges = { # (min_pause_after_scroll, max_pause_after_scroll)
            'safe': (1.0, 2.5),
            'balanced': (0.5, 1.5),
            'aggressive': (0.2, 0.8)
        }

        # Get current mode's settings, defaulting to 'balanced' if mode is unknown
        self.current_delay_multiplier = self.delay_multipliers.get(self.mode, self.delay_multipliers['balanced'])

        current_typing_range = self.typing_delay_ranges.get(self.mode, self.typing_delay_ranges['balanced'])
        self.current_typing_delay_min = current_typing_range[0]
        self.current_typing_delay_max = current_typing_range[1]

        current_watch_range = self.video_watch_time_ranges.get(self.mode, self.video_watch_time_ranges['balanced'])
        self.current_video_watch_min = current_watch_range[0]
        self.current_video_watch_max = current_watch_range[1]

        current_scroll_amount_range = self.scroll_amount_ranges.get(self.mode, self.scroll_amount_ranges['balanced'])
        self.current_scroll_min_pixels = current_scroll_amount_range[0]
        self.current_scroll_max_pixels = current_scroll_amount_range[1]

        current_scroll_pause_range = self.scroll_pause_ranges.get(self.mode, self.scroll_pause_ranges['balanced'])
        self.current_scroll_pause_min = current_scroll_pause_range[0]
        self.current_scroll_pause_max = current_scroll_pause_range[1]

        # Placeholder for like button selector
        self.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER = "//button[@data-testid='like-button-placeholder']" # This is a guess


    def random_delay(self, min_seconds, max_seconds):
        """
        Introduces a random delay, adjusted by the current mode's multiplier.
        :param min_seconds: Base minimum delay in seconds.
        :param max_seconds: Base maximum delay in seconds.
        """
        adj_min = max(0.01, min_seconds * self.current_delay_multiplier) # Ensure non-negative
        adj_max = max(0.02, max_seconds * self.current_delay_multiplier) # Ensure non-negative and min < max
        if adj_min >= adj_max: # Ensure min is strictly less than max
            adj_max = adj_min + 0.01
        time.sleep(random.uniform(adj_min, adj_max))

    def human_type(self, element, text):
        """
        Simulates human-like typing into a web element, with delays adjusted by mode.
        :param element: The Selenium WebElement to type into.
        :param text: The text to type.
        """
        for char in text:
            element.send_keys(char)
            if char == ' ':
                if self.mode == 'safe' and random.random() < 0.10: # 10% chance for safe mode
                    self.random_delay(0.2, 0.5) # These base delays will be multiplied by current_delay_multiplier
                elif self.mode == 'balanced' and random.random() < 0.05: # 5% chance for balanced mode
                    self.random_delay(0.1, 0.3) # These base delays will be multiplied by current_delay_multiplier
                else:
                    # Original char delay if no special space pause
                    time.sleep(random.uniform(self.current_typing_delay_min, self.current_typing_delay_max))
            else:
                # Original char delay for non-space characters
                time.sleep(random.uniform(self.current_typing_delay_min, self.current_typing_delay_max))

    def human_click(self, element):
        """
        Simulates a human-like click on a web element, with delays adjusted by mode.
        :param element: The Selenium WebElement to click.
        """
        # Using random_delay which incorporates the multiplier
        self.random_delay(0.2, 0.5) # Base delays, will be adjusted by random_delay
        element.click()
        self.random_delay(0.2, 0.5) # Base delays, will be adjusted by random_delay

    def watch_video(self):
        """
        Simulates watching a video, with duration adjusted by mode.
        """
        logger.debug(f"Simulating watching video (Mode: {self.mode}). Duration range: {self.current_video_watch_min}-{self.current_video_watch_max}s (before multiplier)")
        self.random_delay(self.current_video_watch_min, self.current_video_watch_max)


    def like_video(self):
        """
        Selecciona aleatoriamente un fingerprint de la lista `self.fingerprints`.

        Returns:
            str/dict/any or None: Un fingerprint de la lista, o None si la lista
                                  `self.fingerprints` está vacía. El tipo exacto
                                  depende de cómo se almacenen los fingerprints.
        """
        logger.debug(f"Attempting to simulate liking a video (Mode: {self.mode}).")
        try:
            # This selector is a placeholder and will likely not work on the actual TikTok page.
            like_button = self.driver.find_element(By.XPATH, self.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER)
            logger.debug(f"Placeholder like button found using selector: {self.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER}")
            self.human_click(like_button)
            logger.info("Placeholder like button clicked successfully.") # More of an info level event
        except Exception as e:
            # Using logger.warning for a non-critical failure of a placeholder action
            logger.warning(f"Could not click placeholder like button (expected for placeholder): {e}")

    def random_scroll(self):
        """
        Selecciona aleatoriamente un proxy de la lista `self.proxies`.

        Returns:
            str or None: Una cadena de proxy (ej. 'ip:port') de la lista, o None
                         si la lista `self.proxies` está vacía.
        """
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def apply_evasion(self, bot):
        """
        Aplica un fingerprint y un proxy rotados a la instancia de bot proporcionada.

        Obtiene un nuevo fingerprint llamando a `self.rotate_fingerprint()` y un
        nuevo proxy llamando a `self.rotate_proxy()`. Luego, si estos valores
        no son None, los asigna al bot utilizando los métodos `bot.assign_fingerprint()`
        y `bot.assign_proxy()`.

        Args:
            bot: Una instancia de un objeto bot que se espera tenga los métodos
                 `assign_fingerprint(fp)` y `assign_proxy(px)`.
        """
        fp = self.rotate_fingerprint()
        px = self.rotate_proxy()

        if fp: # Ensure a fingerprint was returned
            bot.assign_fingerprint(fp)

        if px: # Ensure a proxy was returned
            bot.assign_proxy(px)
