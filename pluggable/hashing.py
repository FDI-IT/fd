import hashlib

def sha_hash(my_path):
    with open(my_path,'r') as my_file:
        sha = hashlib.sha256()
        for chunk in iter(lambda: my_file.read(8192),''):
            sha.update(chunk)
        return sha.hexdigest()
    return None