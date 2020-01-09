import os, errno, logging
from django.conf import settings

LOG_FILE_NAME = os.path.join(settings.LOG_PATH,"%s.log" % __name__)

handler = logging.FileHandler(LOG_FILE_NAME)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)