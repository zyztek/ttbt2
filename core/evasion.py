"""
This module defines the HumanBehaviorSimulator class, which is responsible for
emulating human-like interactions with web elements. These simulations aim to
make automated actions appear more natural and help evade basic bot detection
mechanisms.
"""
import time
import random
from selenium.webdriver.common.by import By
from core.logger import get_logger

# Initialize a logger for this module
logger = get_logger("HumanBehaviorSimulator")

class HumanBehaviorSimulator:
    """
    Simulates human-like behavior for web automation tasks.

    This class provides methods for actions like typing, clicking, scrolling,
    and introducing delays, all of which can be adjusted based on an operational
    mode ('safe', 'balanced', 'aggressive') to vary the intensity and speed
    of interactions.

    Attributes:
        driver: The Selenium WebDriver instance used to interact with the browser.
        mode (str): The current operational mode (e.g., 'safe', 'balanced', 'aggressive'),
                    which influences the behavior of simulation methods.
        delay_multipliers (dict): Multipliers for adjusting base delay times per mode.
        typing_delay_ranges (dict): Min/max character typing delays per mode.
        video_watch_time_ranges (dict): Min/max video watching durations per mode.
        scroll_amount_ranges (dict): Min/max scroll distances in pixels per mode.
        scroll_pause_ranges (dict): Min/max pause durations after scrolling per mode.
        current_delay_multiplier (float): The delay multiplier for the current mode.
        current_typing_delay_min (float): Minimum typing delay for the current mode.
        current_typing_delay_max (float): Maximum typing delay for the current mode.
        current_video_watch_min (float): Minimum video watch time for the current mode.
        current_video_watch_max (float): Maximum video watch time for the current mode.
        current_scroll_min_pixels (int): Minimum scroll distance for the current mode.
        current_scroll_max_pixels (int): Maximum scroll distance for the current mode.
        current_scroll_pause_min (float): Minimum post-scroll pause for the current mode.
        current_scroll_pause_max (float): Maximum post-scroll pause for the current mode.
        LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER (str): A placeholder XPath for a 'like' button.
                                                      This is for demonstration and likely needs
                                                      to be updated for a specific website.
    """
    def __init__(self, driver, mode='balanced'):
        """
        Initializes the HumanBehaviorSimulator.

        Args:
            driver: The Selenium WebDriver instance.
            mode (str, optional): The simulation mode ('safe', 'balanced', 'aggressive').
                                  Defaults to 'balanced'. This mode determines the
                                  aggressiveness and speed of simulated actions.
        """
        self.driver = driver
        self.mode = mode.lower() # Ensure mode is consistently lowercase
        logger.debug(f"HumanBehaviorSimulator initialized with mode: {self.mode}")

        # --- Mode-specific behavioral parameters ---
        # These dictionaries define the base values for different actions per mode.
        # The actual behavior will use values derived from these based on the current `self.mode`.

        self.delay_multipliers = {
            'safe': 1.5,    # Slower actions
            'balanced': 1.0, # Normal actions
            'aggressive': 0.7 # Faster actions
        }
        self.typing_delay_ranges = { # (min_char_delay_seconds, max_char_delay_seconds)
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
            'safe': (200, 500),    # Shorter scrolls
            'balanced': (300, 700),
            'aggressive': (500, 1000) # Longer scrolls
        }
        self.scroll_pause_ranges = { # (min_pause_after_scroll_seconds, max_pause_after_scroll_seconds)
            'safe': (1.0, 2.5),
            'balanced': (0.5, 1.5),
            'aggressive': (0.2, 0.8)
        }

        # --- Derive current operational parameters based on mode ---
        # This section sets up instance attributes for the currently selected mode's
        # behavior, defaulting to 'balanced' settings if an unknown mode is provided.

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

        # Placeholder for a 'like' button selector.
        # This is a generic example and would need to be replaced with an actual,
        # reliable selector for the target website's like button.
        self.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER = "//button[@data-testid='like-button-placeholder']"
        logger.debug(f"Behavior parameters set for mode '{self.mode}': delay_multiplier={self.current_delay_multiplier}, typing_delay=({self.current_typing_delay_min}-{self.current_typing_delay_max})s, etc.")


    def random_delay(self, min_seconds, max_seconds):
        """
        Introduces a random delay, adjusted by the current mode's multiplier.

        The base `min_seconds` and `max_seconds` are scaled by `self.current_delay_multiplier`.
        Ensures delays are not negative and that `min_seconds` is less than `max_seconds`.

        Args:
            min_seconds (float): Base minimum delay in seconds.
            max_seconds (float): Base maximum delay in seconds.
        """
        # Apply the mode-specific multiplier to the base delay range.
        adj_min = min_seconds * self.current_delay_multiplier
        adj_max = max_seconds * self.current_delay_multiplier

        # Ensure delays are practical and valid.
        adj_min = max(0.01, adj_min) # Prevent zero or negative minimum delays.
        adj_max = max(adj_min + 0.01, adj_max) # Ensure max is always greater than min.

        delay = random.uniform(adj_min, adj_max)
        logger.trace(f"Performing random_delay: base=({min_seconds:.2f}-{max_seconds:.2f})s, mode='{self.mode}', multiplier={self.current_delay_multiplier:.2f}, adjusted=({adj_min:.2f}-{adj_max:.2f})s, actual_delay={delay:.2f}s")
        time.sleep(delay)

    def human_type(self, element, text):
        """
        Simulates human-like typing into a web element.

        Types characters one by one with small, randomized delays between each.
        The delay duration is determined by `self.current_typing_delay_min` and
        `self.current_typing_delay_max`.
        Includes a chance for a longer pause after spaces, dependent on the mode,
        to mimic more natural typing rhythm.

        Args:
            element: The Selenium WebElement to type into.
            text (str): The text to type.
        """
        logger.debug(f"Human_type: Typing text '{text[:20]}...' into element. Mode: '{self.mode}'")
        for char_index, char in enumerate(text):
            element.send_keys(char)
            # Determine delay before typing the next character.
            if char == ' ':
                # Higher chance of longer pause after a space in 'safe' or 'balanced' modes.
                if self.mode == 'safe' and random.random() < 0.10: # 10% chance for safe mode
                    logger.trace("Human_type: Special pause after space (safe mode).")
                    self.random_delay(0.2, 0.5) # Base delays, will be multiplied by current_delay_multiplier in random_delay.
                elif self.mode == 'balanced' and random.random() < 0.05: # 5% chance for balanced mode
                    logger.trace("Human_type: Special pause after space (balanced mode).")
                    self.random_delay(0.1, 0.3) # Base delays.
                else:
                    # Default short delay after space if no special pause triggered.
                    time.sleep(random.uniform(self.current_typing_delay_min, self.current_typing_delay_max))
            else:
                # Standard delay for non-space characters.
                time.sleep(random.uniform(self.current_typing_delay_min, self.current_typing_delay_max))

            if (char_index + 1) % 10 == 0: # Log progress every 10 characters for long text
                 logger.trace(f"Human_type: Typed {char_index + 1}/{len(text)} characters.")

    def human_click(self, element):
        """
        Simulates a human-like click on a web element.

        Introduces small, mode-adjusted random delays before and after the click
        action to make it appear less robotic.

        Args:
            element: The Selenium WebElement to click.
        """
        logger.debug(f"Human_click: Attempting to click element. Mode: '{self.mode}'")
        # Use self.random_delay, which already incorporates the mode-specific multiplier.
        # These are base delay values; random_delay will adjust them.
        self.random_delay(0.2, 0.5) # Pre-click delay.
        element.click()
        logger.trace("Human_click: Element clicked.")
        self.random_delay(0.2, 0.5) # Post-click delay.

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
        Simulates liking a video.
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
        Simulates a random scroll action, adjusted by mode.
        """
        scroll_amount = random.randint(self.current_scroll_min_pixels, self.current_scroll_max_pixels)
        logger.debug(f"Simulating random scroll of {scroll_amount} pixels (Mode: {self.mode}). Pause range: {self.current_scroll_pause_min}-{self.current_scroll_pause_max}s (before multiplier)")
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        self.random_delay(self.current_scroll_pause_min, self.current_scroll_pause_max)
