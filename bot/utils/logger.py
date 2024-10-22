import sys
from loguru import logger


logger.remove()
logger.add(sink=sys.stdout, format="<white>{time:HH:mm:ss}</white>"
                                   " | "
                                   "<white><b>{message}</b></white>")
logger = logger.opt(colors=True)

