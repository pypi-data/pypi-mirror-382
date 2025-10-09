import logging


def load_logger():
    logger = logging.getLogger('sync_env')
    logger.setLevel(logging.DEBUG)
    consoleHandler = logging.StreamHandler()
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    return logger
