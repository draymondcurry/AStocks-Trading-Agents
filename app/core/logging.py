import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

from pythonjsonlogger.json import JsonFormatter


def configure_logging(level: str) -> None:
    Path("logs").mkdir(parents=True, exist_ok=True)
    formatter = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    file_handler = RotatingFileHandler("logs/app.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.addHandler(file_handler)
    root.setLevel(level.upper())
