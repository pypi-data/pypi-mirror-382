import json
import logging
import logging.config
from pathlib import Path


def setup_logging():
    """Set up logging according to the config file."""
    file_parent = Path(__file__).parent
    with open(file_parent / 'config.json', 'r', encoding="UTF-8") as config_file:
        config = json.load(config_file)
    logging.config.dictConfig(config)
    logging.basicConfig(filename=file_parent / "logs/report.log")

setup_logging()

def get_logger(name: str):
    """Return logger name."""
    return logging.getLogger(name)
