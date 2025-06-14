"""
Manages and tracks user engagement for the bot.

This module provides the EngagementManager class, which helps in keeping
track of users the bot has already engaged with, preventing redundant
interactions within a session or across sessions if persisted.
"""
from core.logger import get_logger

# Initialize logger for this module
engagement_logger = get_logger(__name__)

class EngagementManager:
    """
    Tracks users with whom the bot has engaged.

    This manager uses a set to store user IDs, providing an efficient way
    to check if an interaction has already occurred with a specific user.

    Attributes:
        engaged_users (set): A set of user IDs that have been engaged with.
    """
    def __init__(self):
        """
        Initializes the EngagementManager with an empty set of engaged users.
        """
        self.engaged_users = set()
        engagement_logger.info("EngagementManager initialized.")

    def engage_user(self, user_id):
        """
        Marks a user as engaged.

        Adds the user's ID to the set of engaged users. If the user_id is None
        or already present, the action is logged accordingly without error.

        Args:
            user_id (str or int): The unique identifier of the user.
        """
        if user_id is None:
            engagement_logger.warning("Attempted to engage with a None user_id.")
            return

        if user_id not in self.engaged_users:
            self.engaged_users.add(user_id)
            engagement_logger.debug(f"User '{user_id}' marked as engaged. Total engaged users: {len(self.engaged_users)}.")
        else:
            engagement_logger.trace(f"User '{user_id}' was already marked as engaged.")

    def has_engaged(self, user_id) -> bool:
        """
        Checks if the bot has already engaged with a specific user.

        Args:
            user_id (str or int): The unique identifier of the user to check.

        Returns:
            bool: True if the user has been engaged with, False otherwise.
                  Returns False if user_id is None.
        """
        if user_id is None:
            engagement_logger.debug("has_engaged called with None user_id, returning False.")
            return False

        engaged = user_id in self.engaged_users
        # Using trace level for this check as it might be called frequently.
        engagement_logger.trace(f"Checking engagement for user '{user_id}': {engaged}.")
        return engaged

    def get_engaged_count(self) -> int:
        """
        Returns the total number of unique users engaged with.

        Returns:
            int: The count of engaged users.
        """
        count = len(self.engaged_users)
        engagement_logger.debug(f"Current engaged user count: {count}.")
        return count

    def clear_engagement_history(self):
        """
        Clears the history of engaged users.
        """
        count_before_clear = len(self.engaged_users)
        self.engaged_users.clear()
        engagement_logger.info(f"Engagement history cleared. {count_before_clear} users were removed from history.")

# Example Usage (for demonstration or testing if this file is run directly):
# if __name__ == "__main__":
#     # Configure logger for direct script run if not already configured by a central setup
#     # from core.logger import setup_logger
#     # setup_logger() # Or use a specific configuration for testing
#
#     manager = EngagementManager()
#     manager.engage_user("user123")
#     manager.engage_user("user456")
#     manager.engage_user("user123") # Engage same user again
#     manager.engage_user(None)      # Try to engage with None
#
#     print(f"Has engaged with user123: {manager.has_engaged('user123')}")
#     print(f"Has engaged with user789: {manager.has_engaged('user789')}")
#     print(f"Has engaged with None: {manager.has_engaged(None)}")
#     print(f"Total engaged users: {manager.get_engaged_count()}")
#
#     manager.clear_engagement_history()
#     print(f"Total engaged users after clearing: {manager.get_engaged_count()}")
#     print(f"Has engaged with user123 after clearing: {manager.has_engaged('user123')}")
