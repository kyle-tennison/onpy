import sys
from loguru import logger
logger.remove()
logger.add(sys.stdout, colorize=True, format="<level>{level: <8}</level> | <level>{message}</level>")


from pyshape.client import Client
