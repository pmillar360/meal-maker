import logging

def intialize_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
def get_logger():

    return logging.getLogger(__name__);

def log(msg: str, level: int = logging.INFO):
    logger = get_logger()

    logger.log(level=level, msg=msg)