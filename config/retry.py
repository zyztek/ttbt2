import time
from config.settings import DEFAULT_RETRY_ATTEMPTS, DEFAULT_RETRY_DELAY_SECS # Added

def retry(func, retries=DEFAULT_RETRY_ATTEMPTS, delay=DEFAULT_RETRY_DELAY_SECS): # Updated defaults
    """
    Retries a function call a specified number of times with a delay between retries.

    Args:
        func (callable): The function to be retried.
        retries (int, optional): The maximum number of attempts.
                                 Defaults to DEFAULT_RETRY_ATTEMPTS from config.settings.
        delay (int, optional): The delay in seconds between retries.
                               Defaults to DEFAULT_RETRY_DELAY_SECS from config.settings.

    Returns:
        The result of the successful function call.

    Raises:
        Exception: The exception from the last attempt if all retries fail.
    """
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(delay)