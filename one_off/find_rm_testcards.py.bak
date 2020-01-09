import os
import subprocess
import hashlib
import fnmatch

from newqc.models import TestCard, RMTestCard

def test():
    for tc in TestCard.objects.filter(large__isnull=False):
        file_name = tc.large.file.name
        print scan_for_barcode(file_name)
    
def scan_for_barcode(path):
    process = subprocess.Popen(
        [
            '/usr/bin/zbarimg',
            '-q', 
            '-Sean13.disable',
            '-Sean8.disable',
            '-Si25.disable',
            '-Scode39.disable',
            '-Scode128.disable',
            path,
        ], 
        shell=False, 
        stdout=subprocess.PIPE)
    process.wait()
    
    if process.returncode != 0:
        hash_path = '/tmp/%s.jpg' % os.path.split(path)[1]
        process = subprocess.Popen(
            [
                '/usr/bin/convert',
                '-quiet',
                '-blur',
                '2',
                '-black-threshold',
                '70%',
                path,
                hash_path,
            ],
        )
        process.wait()
        process = subprocess.Popen(
        [
            '/usr/bin/zbarimg',
            '-q', 
            '-Sean13.disable',
            '-Sean8.disable',
            '-Si25.disable',
            '-Scode39.disable',
            '-Scode128.disable',
            hash_path
        ], 
        shell=False, 
        stdout=subprocess.PIPE)
        process.wait()
        if process.returncode != 0:
            return (process.returncode, process.communicate()[0])
        # TODO
        # Error handling code here
        #  -crop 500x500+1950x500
        # -blur 2
        # -black-threshold 70%
    try:
        scan_value_raw = process.communicate()[0]
        scan_value = scan_value_raw.split(':')[1]
        return (0, scan_value)
    except Exception as e:
        return (0, process.communicate()[0])