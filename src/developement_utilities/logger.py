import logging
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "log_files"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Normaler Logger
log_file = LOG_DIR / f"run_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=log_file,
    filemode="w",
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

performance_logger = logging.getLogger("performance")
performance_logger.setLevel(logging.INFO)
performance_logger.propagate = False

performance_file = LOG_DIR / f"performance_{timestamp}.log"

handler = logging.FileHandler(performance_file, mode="w")
handler.setFormatter(logging.Formatter(
    LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
))

performance_logger.addHandler(handler)