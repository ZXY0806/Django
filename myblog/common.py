import hashlib


def hash_it(str, salt='this is a salt'):
    h1 = hashlib.sha256()
    str += salt
    h1.update(str.encode())
    return h1.hexdigest()


