import os
import sys
import logging
import datetime
import tempfile
from logging import Logger
from typing import Dict, Tuple, Optional

_contexts: Dict[str, Tuple[Logger, str]] = {}

def _default_log_dir() -> str:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return os.path.join(base, "M1PPLauncher", "logs")
    return os.path.join(tempfile.gettempdir(), "M1PPLauncher-logs")


def setup(context: str, log_dir: Optional[str] = None) -> str:

    if context in _contexts:
        return _contexts[context][1]

    if not log_dir:
        log_dir = _default_log_dir()

    os.makedirs(log_dir, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(log_dir, f"m1pp-{context}-{ts}.log")

    logger = logging.getLogger(f"m1pp.{context}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        fmt = logging.Formatter(
            fmt="(%(asctime)s) [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        #this could be tidier but I couldn't be bothered to add it. 
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

        if getattr(sys, "stdout", None) is not None and hasattr(sys.stdout, "write"):
            sh = logging.StreamHandler(stream=sys.stdout)
            sh.setLevel (logging.INFO)
            sh.setFormatter(fmt)
            logger.addHandler(sh)

    _contexts[context] = (logger, log_path)
    
    def _excepthook(exc_type, exc, tb):
        try:
            logger.critical("Unhandled exception", exc_info=(exc_type, exc, tb))
        finally:
            sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _excepthook

    logger.info(f"Logger initialized. context={context} path={log_path}")
    return log_path


def get_logger(context: str) -> Logger:
    if context not in _contexts:
        setup(context)
    return _contexts[context][0]


def get_log_path(context: str) -> str:
    if context not in _contexts:
        setup(context)
    return _contexts[context][1]
