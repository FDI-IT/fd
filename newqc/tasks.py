import os, errno, logging

from celery.task import task

from newqc.documents import ImportBCDoc

# set up logging
LOG_PATH = '/var/log/django/'
LOG_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
try:
    os.makedirs(LOG_PATH)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
        pass
    else:
        raise
LOG_FILENAME = '/var/log/django/scan_docs.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, formatter=LOG_FORMATTER)

@task()
def walk_scanned_docs(walk_paths=['/srv/samba/tank/scans/qccards','/srv/samba/tank/scans/barcode_docs','/srv/samba/tank/scans/batchsheets']):
    logger = logging.getLogger()
    for scanned_doc in file_walker(walk_paths):
        logger.info("Importing %s " % full_file_path)
        ir = ImportBCDoc(full_file_path)
                    
def file_walker(walk_paths):
    """Iterates through walk_paths and returns the full file path of any
    jpg or png files.
    """
    for wp in walk_paths:
        for root, dirnames, filenames in os.walk(wp):
            for filename in filenames:
                if filename.lower().endswith(('jpg','png')):
                    yield os.path.join(root,filename)