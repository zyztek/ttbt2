import time
import random
# Assuming selenium's By is needed for some interactions if methods were more complex
# from selenium.webdriver.common.by import By

class HumanBehaviorSimulator:
    def __init__(self, driver):
        self.driver = driver

    def random_delay(self, min_seconds, max_seconds):
        delay = random.uniform(min_seconds, max_seconds)
        print(f"[SIM_BEHAVIOR] Delaying for {delay:.2f} seconds.")
        time.sleep(delay)

    def human_type(self, element, text):
        print(f"[SIM_BEHAVIOR] Typing '{text[:20]}...' into element {element}.")
        # In a real implementation, this would use element.send_keys with delays
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15)) # Simulate typing speed
        # element.send_keys(text)

    def human_click(self, element):
        print(f"[SIM_BEHAVIOR] Clicking element {element}.")
        # In a real implementation, might add mouse movement simulation before click
        element.click()

    def watch_video(self):
        # Simulate watching a video for a random duration
        watch_time = random.uniform(10, 30) # e.g., 10-30 seconds
        print(f"[SIM_BEHAVIOR] 'Watching video' for {watch_time:.2f} seconds.")
        self.random_delay(watch_time, watch_time) # Use random_delay for actual sleep

    def like_video(self):
        print(f"[SIM_BEHAVIOR] 'Liking video'.")
        # Placeholder: In a real scenario, this would find and click a like button.
        # e.g., self.driver.find_element(By.XPATH, "//button[@aria-label='like']").click()
        pass

    def random_scroll(self):
        scroll_amount = random.randint(200, 800)
        print(f"[SIM_BEHAVIOR] Scrolling by {scroll_amount} pixels.")
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        self.random_delay(1, 3) # Delay after scroll
