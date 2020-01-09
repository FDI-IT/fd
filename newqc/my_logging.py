import os, errno, logging
from django.conf import settings

PACKAGE_NAME = "newqc"
LOG_FILE_NAME = os.path.join(settings.LOG_PATH,"%s.log" % PACKAGE_NAME)

handler = logging.FileHandler(LOG_FILE_NAME)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(PACKAGE_NAME)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def get_logger():
    return logger