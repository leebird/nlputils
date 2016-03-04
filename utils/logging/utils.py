import logging


def get_logger(name):
    # Create console handler and set level to INFO.
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)        

    # Create formatter.
    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')

    # Add formatter to ch
    ch.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    return logger
