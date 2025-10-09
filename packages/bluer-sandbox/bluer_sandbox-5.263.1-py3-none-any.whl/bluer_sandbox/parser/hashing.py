import hashlib


def hash_of(string: str) -> str:
    sha_256 = hashlib.sha256()

    sha_256.update(string.encode())

    return sha_256.hexdigest()
