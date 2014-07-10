import os, sys, errno, logging

"""Setting up logging"""

LOG_PATH = '/var/log/django/'
try:
    os.makedirs(LOG_PATH)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
        pass
    else:
        raise
LOG_FILENAME = '/var/log/django/access.log'

LOG_FILE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s: %(message)s"

logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format=LOG_FILE_FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()
#logger.setFormatter(LOG_FILE_FORMAT)



#add a log handler that prints to stdout

STDOUT_LOG_FORMAT = logging.Formatter('%(message)s') 

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(STDOUT_LOG_FORMAT)

logger.addHandler(log_handler)