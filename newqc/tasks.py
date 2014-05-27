import os

import fnmatch

from celery.task import task

from newqc.documents import ImportBCDoc, exc_directory, move_exc_image

@task()
def walk_scans_qccards(walk_paths=['/srv/samba/tank/scans/qccards',]):
    returns = []
    if not os.path.exists(exc_directory):
        os.makedirs(exc_directory)
    for wp in walk_paths:
        for root, dirnames, filenames in os.walk(wp):
            for filename in fnmatch.filter(filenames, '*.jpg'):
                full_file_path = os.path.join(root,filename)
                print "debug: Attempting import of %s " % full_file_path
                try:
                    import_result = ImportBCDoc(full_file_path)
                    returns.append(import_result)
                    print "info: Imported %s" % full_file_path
                except Exception as e:
                    print "warn: Failed to import %s -- %s: %s" % (full_file_path, type(e), e)
                    move_exc_image(full_file_path)
    return returns

