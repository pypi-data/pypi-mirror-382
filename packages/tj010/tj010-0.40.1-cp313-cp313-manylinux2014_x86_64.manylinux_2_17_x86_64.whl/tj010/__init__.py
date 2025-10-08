__author__ = 'Kangkang Zhang'
__version__ = '0.40.1'

import logging

STD_LOGGING_LEVEL = logging.INFO
FILE_LOGGING_LEVEL = logging.ERROR
LOGGING_MSG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'
LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def __set_logger():
    logging.basicConfig(level = logging.INFO, format = '[%(asctime)s] [%(levelname)s] %(message)s', datefmt = '%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('tj010')
    logger.STD_LOGGING_LEVEL = STD_LOGGING_LEVEL
    logger.FILE_LOGGING_LEVEL = FILE_LOGGING_LEVEL
    std_handler = logging.StreamHandler()
    std_handler.setLevel(logger.STD_LOGGING_LEVEL)
    return logger

logger = __set_logger()
logger.info("mpccore initialized.")
logger.info(f"tj010 version = {__version__}")

logging.getLogger('matplotlib').setLevel(logging.ERROR)
