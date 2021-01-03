import math, random, os
from config import Config

def get_paths():
    """
    Calls the Config function to retrieve the namespace file paths 
    from the yml config file. This function returns an array with
    response: 
                [0] the orman.key path and 
                [1] the namespace.orman file path
    """
    paths = Config()
    os.environ["local_str_key_path"] = paths['local_key_path']
    os.environ["local_namespace_path"] = paths['local_namespace_path']
    return paths['local_key_path'], paths["local_namespace_path"]

def convert_size(size_bytes):
    """
    Completely useless, converts bytes to human readable sizes
    for pretty printing
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def randbytes(n):
    """
    Used for generating random bytes, I needed a way to fill up
    namespaces with random data to test compression, encryption, etc
    """
    for _ in range(n):
        yield random.getrandbits(8)

def delete_local_namespace():
    """
    Deletes namespace files, pretty destructive, it deletes any 
    path returned from the get_paths function
    """
    for f in get_paths():
        os.remove(f)