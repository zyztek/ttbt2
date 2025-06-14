"""
Configuration settings for the TikTok Bot application.

This module defines various settings as module-level constants,
making them easily accessible throughout the application.
It includes general bot behavior, API keys (via environment variables),
detailed behavior profiles for different operational modes, Flask app settings,
and default retry mechanism parameters.
"""
import os

# --- Environment-loaded Settings ---
# Sensitive keys or keys that might change per deployment environment
# should be loaded from environment variables.
TIKTOK_API_KEY = os.getenv("TIKTOK_API_KEY", "") # Example: API key for external services

# --- General Bot Settings ---
DEFAULT_BOT_MODE = "balanced" # Default operational mode for the bot if not specified
MAX_VIEWS_DEFAULT_ARG = 5000  # Default value for --max-views argument in main.py
MAX_VIEWS_FALLBACK = 50       # Fallback for TikTokBot if MAX_VIEWS_PER_HOUR env var is missing/invalid
LIKE_PROBABILITY = 0.65       # Probability (0.0 to 1.0) of liking a video during organic actions
INTER_ACTION_CYCLE_PAUSE_RANGE_SECS = (8, 15)  # (min_seconds, max_seconds) pause between full action cycles

# --- Behavior Profiles ---
# Defines detailed behavior parameters for different operational modes ('safe', 'balanced', 'aggressive').
# These profiles are used by HumanBehaviorSimulator to adjust action timings and patterns.
BEHAVIOR_PROFILES = {
    "safe": {
        "delay_multiplier": 1.5,  # General multiplier for random_delay calls
        "typing_delay_range_secs": (0.10, 0.25),  # (min_char_delay, max_char_delay)
        "space_pause_chance": 0.10,  # Chance (0.0 to 1.0) of a longer pause after typing a space
        "space_pause_duration_range_secs": (0.2, 0.5), # Duration for the special space pause
        "video_watch_time_range_secs": (10, 25), # (min_watch_time, max_watch_time)
        "click_base_delay_range_secs": (0.2, 0.5), # Base range for pre/post click delays in human_click
        "scroll_amount_range_pixels": (200, 500), # (min_scroll_pixels, max_scroll_pixels)
        "scroll_pause_duration_range_secs": (1.0, 2.5) # (min_pause, max_pause) after a scroll action
    },
    "balanced": {
        "delay_multiplier": 1.0,
        "typing_delay_range_secs": (0.05, 0.15),
        "space_pause_chance": 0.05,
        "space_pause_duration_range_secs": (0.1, 0.3),
        "video_watch_time_range_secs": (5, 15),
        "click_base_delay_range_secs": (0.2, 0.5), # Kept same as safe, can be tuned
        "scroll_amount_range_pixels": (300, 700),
        "scroll_pause_duration_range_secs": (0.5, 1.5)
    },
    "aggressive": {
        "delay_multiplier": 0.7, # Faster actions
        "typing_delay_range_secs": (0.02, 0.08),
        "space_pause_chance": 0.0, # No special pause after spaces for aggressive mode
        "space_pause_duration_range_secs": (0.0, 0.0), # Not applicable
        "video_watch_time_range_secs": (3, 8), # Shorter watch times
        "click_base_delay_range_secs": (0.1, 0.3), # Shorter base click delays
        "scroll_amount_range_pixels": (500, 1000), # Longer, faster scrolls
        "scroll_pause_duration_range_secs": (0.2, 0.8) # Shorter pauses after scroll
    }
}

# --- Flask App Settings (for api/app.py and main.py) ---
FLASK_HOST = "0.0.0.0"  # Host for the Flask development server
FLASK_PORT = 5000       # Port for the Flask development server

# --- Retry Mechanism Settings (intended for a utility like config/retry.py if implemented) ---
DEFAULT_RETRY_ATTEMPTS = 3    # Default number of retry attempts for an operation
DEFAULT_RETRY_DELAY_SECS = 2  # Default delay in seconds between retry attempts

# --- File Paths (centralized for easier management if needed) ---
# Example: (ensure these paths are correct for your project structure if used)
# ACCOUNTS_FILE_PATH = "accounts.json"
# SELECTORS_FILE_PATH = "selectors.json"
# PROXIES_FILE_PATH = "proxies/proxies.json"
# FINGERPRINTS_FILE_PATH = "fingerprints/fingerprints.json"

# --- Logging Configuration ---
# Example: (if you want to centralize basic logging config here)
# LOG_LEVEL = "INFO" # Default log level (e.g., "DEBUG", "INFO", "WARNING")
# LOG_FILE_PATH = "logs/bot.log" # Path for log file output
# LOG_ROTATION_SIZE = "10 MB" # Max size before log rotation
# LOG_RETENTION_POLICY = "7 days" # How long to keep logs

# Note: DB_PATH was removed as per the plan. If database functionality is added later,
# its configuration can be placed here.
