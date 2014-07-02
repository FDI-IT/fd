import os, errno, logging

from celery.task import task

from newqc.documents import ImportBCDoc

# set up logging
LOG_PATH = '/var/log/django/'
try:
    os.makedirs(LOG_PATH)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
        pass
    else:
        raise
LOG_FILENAME = '/var/log/django/scan_docs.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
logger = logging.getLogger()

@task()
def walk_scans_qccards(walk_paths=['/srv/samba/tank/scans/qccards','/srv/samba/tank/scans/barcode_docs']):
    for wp in walk_paths:
        for root, dirnames, filenames in os.walk(wp):
            for filename in filenames:
                if filename.lower().endswith(('jpg','png')):
                    full_file_path = os.path.join(root,filename)
                    logger.info("Attempting import of %s " % full_file_path)
                    ir = ImportBCDoc(full_file_path)
                    logger.info("Imported %s" % full_file_path)

