import os.path, pickle, json, os, requests
from os import path
from .local_encryption import decrypt, encrypt, load_key

from .tools import get_paths

def init_space_type(space):
    """
    When loading spaces we're looking for a dict, this 
    function takes bytes or string and converts it to a dictionary
    if the input is bytes, it decodes first and then calls itself.
    The function itself is a bit wasteful and overkill but it is to be
    used as the single point of control for namespace I/O types.
    
    """
    if type(space) == bytes:
        try:
            space = space.decode()
        except:
            print("Unable to decode namespace. Invalid namespace bytes.")
            raise
        init_space_type(space)
    if type(space) == str:
        try:
            space = json.loads(space)
        except:
            print("Unable to load json. Invalid namespace string.")
            raise
    if type(space) == dict:
        return space
    return space

def check_lspace():
    """
    Check if you have a orman.key file for decrypting namespace.orman.
    Returns True or False
    """
    get_paths()
    if path.exists( os.environ["local_str_key_path"] ) == True:
        return True
    return False

def load_space():
    """
    This uses environment variables to get 
    the path of your namespace files. Loads them using pickle and
    decrypts using your local secret key.
    This function takes no inputs and it 
    returns a local namespace as dict
    """
    paths = get_paths()
    local_str_key_path = os.environ["local_str_key_path"] 
    local_namespace_path = os.environ["local_namespace_path"]

    if path.exists(local_namespace_path) == False:
        print("Unable to load namespace, check path")
        return False

    if path.exists(local_str_key_path) == False:
        load_key()

    encrypted_namespace = pickle.load( open( local_namespace_path, "rb" ) )
    namespace = decrypt(encrypted_namespace)

    if type(namespace) != 'dict':
        namespace = init_space_type( namespace )

    os.environ["privKey"] = namespace["privKey"]
    os.environ["pubKey"] = namespace["pubKey"]

    return namespace

def save_lspace(namespace, password=None):
    """
    This function expects namespace as a string but it will accept dict.
    It encrypts the string (which is your local namespace) and
    saves it to your namespace.orman file. If no password is 
    provided, it uses the existing local secret key. 
    
    If you wanted to encrypt your namespace locally and not use 
    your existing key file; for some weird reason. You could override password 
    here. 
    
        WARNING:    Overriding password here may 
                    cause you to lose all your data.

        This does NOT modify local key file. Therefore decrypt will 
        show a mismatch next time you load your namespace.

        You'll need to re-create a key file using the same password 
        you entered here before you can decrypt your namespace.

        Again, that is because this function does NOT update the key file. 
        So you'll have an encrypted namespace.orman file with a key other than
        what is stored in orman.key. The password used to encrypt, decrypt must 
        be hashed first.

        So if you override password here then I assume you know what you're 
        doing. 
    """
    paths = get_paths()
    local_namespace_path = os.environ["local_namespace_path"]

    if type(namespace) == dict:
        namespace = json.dumps(namespace)

    encrypted_namespace = encrypt(namespace, password)
    pickle.dump( 
        encrypted_namespace , 
        open( 
            os.environ["local_namespace_path"], 
            "wb" 
        ) 
    )
    return namespace

