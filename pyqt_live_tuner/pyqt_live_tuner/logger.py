import logging
import os

# Create a global logger instance
logger = logging.getLogger("CameraTuner")
logger.setLevel(logging.DEBUG)  # Default to DEBUG; can be overridden

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(os.getenv("LOG_LEVEL_CONSOLE", "INFO").upper())

# File handler
log_file = os.getenv("LOG_FILE", "camera_tuner.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(os.getenv("LOG_LEVEL_FILE", "DEBUG").upper())

# Log format
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Attach handlers (only once)
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

logger.info("Logger initialized. Console level: %s, File level: %s", 
            console_handler.level, file_handler.level)
