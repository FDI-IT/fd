import os, errno, logging
from datetime import timedelta

from django.core.cache import cache

from celery.task import task

from newqc.documents import ImportBCDoc

# set up logging
LOG_PATH = '/var/log/django/'
LOG_FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
try:
    os.makedirs(LOG_PATH)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
        pass
    else:
        raise
LOG_FILENAME = '/var/log/django/scan_docs.log'
LOG_FILE_HANDLER = logging.FileHandler(LOG_FILENAME)
LOG_FILE_HANDLER.setLevel(logging.INFO)
LOG_FILE_HANDLER.setFormatter(LOG_FORMATTER)

LOCK_EXPIRE = 60 * 20 # lock expires in 20 minutes

@task()
def walk_scanned_docs(walk_paths=['/srv/samba/tank/scans/qccards','/srv/samba/tank/scans/barcode_docs','/srv/samba/tank/scans/batchsheets']):
    logger = logging.getLogger()
    
    lock_id = "newqc.tasks.walk_scanned_docs.lock"
    acquire_lock = lambda: cache.add(lock_id, 'true', LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)
    
    if acquire_lock():
        logger.warn("Initiating walk_scanned_docs")
        try:
            for scanned_doc_path in file_walker(walk_paths):
                ir = ImportBCDoc(scanned_doc_path)
        finally:
            release_lock()
        
    else:
        logger.warn("Lock already in place")

        
@task()
def log_test():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("LOG TEST!")
                    
def file_walker(walk_paths):
    """Iterates through walk_paths and returns the full file path of any
    jpg or png files.
    """
    for wp in walk_paths:
        for root, dirnames, filenames in os.walk(wp):
            for filename in filenames:
                if filename.lower().endswith(('jpg','png')):
                    yield os.path.join(root,filename)
