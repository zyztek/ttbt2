from loguru import logger
import os

LOG_PATH = os.getenv("LOG_PATH", "logs/ttbt1.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logger.add(LOG_PATH, rotation="1 MB", retention="7 days", level="INFO", enqueue=True)
logger.add(lambda msg: print(msg, end=""), level="INFO")  # Console

def get_logger(name=None):
    return logger.bind(name=name)