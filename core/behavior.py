import time
import random
# Assuming selenium's By is needed for some interactions if methods were more complex
from selenium.webdriver.common.by import By # Uncommented import

class HumanBehaviorSimulator:
    def __init__(self, driver):
        self.driver = driver

    def random_delay(self, min_seconds, max_seconds):
        delay = random.uniform(min_seconds, max_seconds)
        print(f"[SIM_BEHAVIOR] Delaying for {delay:.2f} seconds.")
        time.sleep(delay)

    def human_type(self, element, text, click_first=False):
        """
        Simulates human-like typing into a web element.

        Args:
            element: The Selenium WebElement to type into.
            text (str): The text to type.
            click_first (bool, optional): If True, attempts to click the element
                                          before typing. Defaults to False.
        """
        print(f"[SIM_BEHAVIOR] Preparing to type into element {element}.")
        if click_first:
            try:
                element.click()
                self.random_delay(0.2, 0.5) # Short delay after click
            except Exception as e:
                print(f"[SIM_BEHAVIOR] Could not click element before typing: {e}")

        self.random_delay(0.3, 0.8) # Initial delay before typing starts

        # Replace newline for cleaner log, but type the original text
        log_text = text.replace(chr(10), '\\n') # For multiline text in logs
        print(f"[SIM_BEHAVIOR] Typing '{log_text[:20]}...'")

        for char_idx, char in enumerate(text):
            element.send_keys(char)
            # Default short delay
            char_delay = random.uniform(0.05, 0.15)
            # Chance for a slightly longer pause (e.g., every 5-10 chars or randomly)
            if random.random() < 0.1: # 10% chance of a longer pause
                char_delay += random.uniform(0.1, 0.3)
            time.sleep(char_delay)
        print(f"[SIM_BEHAVIOR] Finished typing.")

    def human_click(self, element):
        print(f"[SIM_BEHAVIOR] Clicking element {element}.")
        # In a real implementation, might add mouse movement simulation before click
        element.click()

    def watch_video(self, min_duration=10, max_duration=30):
        """
        Simulates watching a video for a variable duration, with potential
        intermittent small actions like minor scrolls or conceptual mouse movements.

        Args:
            min_duration (int/float, optional): Minimum duration to watch the video. Defaults to 10s.
            max_duration (int/float, optional): Maximum duration to watch the video. Defaults to 30s.
        """
        total_watch_time = random.uniform(min_duration, max_duration)
        print(f"[SIM_BEHAVIOR] Starting to 'watch video' for approximately {total_watch_time:.2f} seconds.")

        num_segments = random.randint(1, 3) # Watch in 1 to 3 segments
        if num_segments == 0 : num_segments = 1 # ensure at least one segment
        time_per_segment = total_watch_time / num_segments

        for i in range(num_segments):
            segment_watch_time = random.uniform(time_per_segment * 0.8, time_per_segment * 1.2)
            print(f"[SIM_BEHAVIOR] Watching segment {i+1}/{num_segments} for {segment_watch_time:.2f}s.")
            # Directly use time.sleep for the core segment watching, random_delay can be used for sub-actions
            time.sleep(segment_watch_time)

            if i < num_segments - 1: # Don't do actions after the last segment of watching
                if random.random() < 0.3: # 30% chance of a small scroll
                    temp_scroll_amount = random.randint(50, 150)
                    print(f"[SIM_BEHAVIOR] Minor scroll ({temp_scroll_amount}px) during video watch.")
                    try:
                        self.driver.execute_script(f"window.scrollBy(0, {temp_scroll_amount});")
                        self.random_delay(0.5, 1.5) # Use self.random_delay for action pauses
                    except Exception as e:
                        print(f"[SIM_BEHAVIOR] Error during minor scroll: {e}")

                if random.random() < 0.5: # 50% chance of conceptual mouse movement
                    print(f"[SIM_BEHAVIOR] Simulating mouse movement during video watch.")
                    self.random_delay(0.2, 0.5) # Use self.random_delay for action pauses

        print(f"[SIM_BEHAVIOR] Finished 'watching video'.")

    def like_video(self):
        print(f"[SIM_BEHAVIOR] Attempting to 'Like video'.")
        try:
            # Hypothetical XPath for a like button
            like_button_xpath = "//button[@aria-label='like' or @data-testid='like-button']"
            like_button = self.driver.find_element(By.XPATH, like_button_xpath)
            like_button.click()
            print(f"[SIM_BEHAVIOR] Clicked 'like' button.")
            self.random_delay(0.5, 1.5) # Small delay after action
        except Exception as e:
            print(f"[SIM_BEHAVIOR] Could not 'like' video: {e}")

    def random_scroll(self):
        scroll_amount = random.randint(200, 800)
        print(f"[SIM_BEHAVIOR] Scrolling by {scroll_amount} pixels.")
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        self.random_delay(1, 3) # Delay after scroll
