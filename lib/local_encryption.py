import os, base64
from os import path 
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

def gen_local_key(password):
    """
    Takes password as string, converts to bytes and hashes it. 
    The hashed password is later used to encrypt your namespace
    locally. 
    """
    if type(password) == str:
        password = password.encode()
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(password)
    key = base64.urlsafe_b64encode(digest.finalize())
    return key

def save_key(key):
    """
    Takes key as string, which is your hashed password and saves
    it to you orman.key file
    """
    with open( os.environ["local_str_key_path"], "wb") as key_file:
        key_file.write(key)
    return key

def load_key(password=None):
    """
    Loads your orman.key containing your hashed password
    and returns it as string
    """
    if path.exists( os.environ["local_str_key_path"] ) == False:
        if password == None:
            password = input("Missing key file, enter password: ")
        key = save_key( gen_local_key(password) )
        return key
    key = open( 
        os.environ["local_str_key_path"], 
        "rb"
    ).read()
    return key

def encrypt(string, password=None):
    """ 
    Using Fernet, this function encrypts a string. If
    no password is provided. It will use the one stored in
    your orman.key file or one will be generated in the load_key 
    function
    """
    string = string.encode()
    f = Fernet( load_key(password) )
    return f.encrypt( bytes(string) )

def decrypt(string):
    f = Fernet(load_key())
    try:
        decrypted = f.decrypt(bytes(string))
    except:
        print("Unable to decrypt local namespace, try different key")
        quit()
    return decrypted