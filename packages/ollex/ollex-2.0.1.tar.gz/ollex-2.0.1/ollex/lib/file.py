"""File utilities."""

from hashlib import sha256

BUFSIZ = 65536


# ------------------------------------------------------------------------------
def sha256_file(filename: str) -> str:
    """Calculate the sha256 hash of a file and return the hex digest."""

    sha = sha256()
    with open(filename, 'rb') as fp:
        while True:
            if not (buf := fp.read(BUFSIZ)):
                break
            print(buf)
            sha.update(buf)

    return sha.hexdigest()
