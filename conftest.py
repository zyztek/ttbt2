"""
Pytest configuration for logging setup and test fixtures.
"""
import logging
import pytest

@pytest.fixture(autouse=True)
def setup_logging(caplog):
    """
    Set up logging for all tests to ensure log messages are captured by caplog.
    """
    # Set all loggers to DEBUG level for tests
    caplog.set_level(logging.DEBUG)
    
    # Specifically configure the core module loggers
    core_loggers = [
        'core.account_manager',
        'core.behavior',
        'core.bot',
        'core.bot_engine', 
        'core.config_loader',
        'core.evasion',
        'core.logger',
        'TikTokBot'
    ]
    
    for logger_name in core_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        # Ensure propagation so caplog can capture messages
        logger.propagate = True
