import logging
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "log_files"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

log_file = LOG_DIR / f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=log_file,
    filemode="w",
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)