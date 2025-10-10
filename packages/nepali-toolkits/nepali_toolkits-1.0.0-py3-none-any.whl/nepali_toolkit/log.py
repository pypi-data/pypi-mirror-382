import logging, os
def get_logger(name: str) -> logging.Logger:
    lvl = os.getenv("NEPALI_TOOLKIT_LOGLEVEL", "WARNING").upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(h)
    logger.setLevel(lvl)
    return logger
