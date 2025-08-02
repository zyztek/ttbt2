import time
import random
from selenium.webdriver.common.by import By
from core.logger import get_logger
from config.settings import BEHAVIOR_PROFILES, DEFAULT_BOT_MODE

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
        self.mode = mode.lower()  # Ensure mode is consistently lowercase
        logger.info(f"HumanBehaviorSimulator initializing with mode: {self.mode}")

        # Fetch the behavior profile for the current mode, or default if mode is invalid
        current_profile = BEHAVIOR_PROFILES.get(self.mode, BEHAVIOR_PROFILES[DEFAULT_BOT_MODE])
        if self.mode not in BEHAVIOR_PROFILES:
            logger.warning(f"Mode '{self.mode}' not found in BEHAVIOR_PROFILES. Using default mode '{DEFAULT_BOT_MODE}'.")
            self.mode = DEFAULT_BOT_MODE  # Update mode to default if it was invalid

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

        # Placeholder for like button selector
        self.LIKE_BUTTON_SELECTOR_XPATH_PLACEHOLDER = "//button[@data-testid='like-button-placeholder']"

    def random_delay(self, min_seconds, max_seconds):
        """
        Introduces a random delay, adjusted by the current mode's multiplier.
        
        Args:
            min_seconds: Base minimum delay in seconds.
            max_seconds: Base maximum delay in seconds.
        """
        adj_min = max(0.01, min_seconds * self.current_delay_multiplier)  # Ensure non-negative
        adj_max = max(0.02, max_seconds * self.current_delay_multiplier)  # Ensure non-negative and min < max
        if adj_min >= adj_max:  # Ensure min is strictly less than max
            adj_max = adj_min + 0.01
        time.sleep(random.uniform(adj_min, adj_max))

    def human_type(self, element, text):
        """
        Simulates human-like typing into a web element, with delays adjusted by mode.
        
        Args:
            element: The Selenium WebElement to type into.
            text: The text to type.
        """
        for char in text:
            element.send_keys(char)
            if char == ' ':
                if random.random() < self.current_space_pause_chance:
                    self.random_delay(self.current_space_pause_min_duration, self.current_space_pause_max_duration)
                else:
                    # Original char delay if no special space pause
                    time.sleep(random.uniform(self.current_typing_delay_min, self.current_typing_delay_max))
            else:
                # Original char delay for non-space characters
                time.sleep(random.uniform(self.current_typing_delay_min, self.current_typing_delay_max))

    def human_click(self, element):
        """
        Simulates a human-like click on a web element, with delays adjusted by mode.
        
        Args:
            element: The Selenium WebElement to click.
        """
        logger.debug(f"Human_click: Attempting to click element. Mode: '{self.mode}'")
        # Use self.random_delay, which incorporates the mode-specific multiplier.
        self.random_delay(self.current_click_min_delay, self.current_click_max_delay)  # Pre-click delay.
        element.click()
        logger.trace("Human_click: Element clicked.")
        self.random_delay(self.current_click_min_delay, self.current_click_max_delay)  # Post-click delay.

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
            logger.debug("Placeholder like button found.")
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
