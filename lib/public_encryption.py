import sys, json, ast, time, hashlib, os
from Crypto.PublicKey import RSA
from Cryptodome.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5   
from Cryptodome.Random import get_random_bytes
from .tools import convert_size
from secrets import token_urlsafe
from base64 import b64encode as e64
from base64 import b64decode as d64

def encrypt(space , key):
    """
    Used to encrypt namespaces as string.

    This takes a string and encrypts it using the provided key.
    Do not edit this function for any reason. It could cause 
    loss to all you namespace data locally and cloud if something goes
    wrong with your encryption

    Returns encrypted string
    """
    salt = get_random_bytes(
        AES.block_size
    )
    private_key = hashlib.scrypt(
        key.encode(),
        salt=salt,
        n=(2 ** 14),
        r=8, p=1,
        dklen=32
    )
    cipher_config = AES.new(private_key, AES.MODE_GCM)
    sipher, tag = cipher_config.encrypt_and_digest( 
        bytes( space, 'utf-8' ) 
    )
    eD = {
        'sipher': e64(sipher).decode('utf-8'),
        'salt': e64(salt).decode('utf-8'),
        'nonce': e64(cipher_config.nonce).decode('utf-8'),
        'tag': e64(tag).decode('utf-8'),
    }
    encrypted_space_str = ( 
        "%s*%s*%s*%s" % (
            eD['sipher'],
            eD['salt'],
            eD['nonce'],
            eD['tag']
        )
    )
    return encrypted_space_str

def decrypt(space, key):
    """
    Used to decrypt namespaces as string.

    This takes a string and encrypts it using the provided key.
    Do not edit this function for any reason. It could cause 
    loss to all you namespace data locally and cloud if something goes
    wrong with your encryption

    Returns decrypted string
    """
    space = space.split('*')
    space_dict = {
        'sipher': space[0],
        'salt': space[1],
        'nonce': space[2],
        'tag': space[3],
    }
    for sS in space_dict:
        sD = d64( space_dict[sS] )
        exec( ( "%s=%s" % (sS,sD) ), globals() )
    private_key = hashlib.scrypt(
        key.encode(),
        salt=salt,
        n=(2 ** 14),
        r=8, p=1,
        dklen=32
    )
    cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)
    decrypted = cipher.decrypt_and_verify(sipher, tag)
    return decrypted.decode('UTF-8')

def generate_keys():
    """
    Used to generate public and private RSA keys
    returns both as an array. These keys are used to encrypt 
    the aeskeys, which are then used to encrypt the namespace string.
    """
    key = RSA.generate(2048)
    public_key = ( key.publickey().exportKey() ).decode()
    private_key = ( key.exportKey('PEM') ).decode()   
    os.environ["pubKey"] = public_key
    os.environ["privKey"] = private_key
    return [public_key, private_key]

def decrypt_message(privKey, cipher):
    """
    Used to decrypt the aeskey, which is used to
    encrypt the entire namespace
    """
    keyPriv = RSA.importKey(privKey) 
    Cipher = Cipher_PKCS1_v1_5.new(keyPriv)
    try:
        message = Cipher.decrypt(cipher, None).decode()
    except:
        print("      Message failed to decrypt: %s" % (cipher))
        raise
    return message

def encrypt_message(pubKey, message):
    """
    Used to encrypt the aeskey, which is used to
    encrypt the entire namespace
    """
    keyPub = RSA.importKey(pubKey)  
    cipher = Cipher_PKCS1_v1_5.new(keyPub)     
    return cipher.encrypt(message.encode())

def encrypt_space(space, pubKey):
    """
    Used as a caller to encrypt namespaces.
    Takes namespace as a dict.

    It calls encrypt, to encrypt the namesace
     using a random generated aeskey. 
     
    The aeskey is then encrypted using your 
    pubKey and stored with the encrypted 
    namespace string.

    Returns dict with namespace
    and aeskey as encrypted strings
    """
    aeskey = token_urlsafe(32)
    nspace_str = json.dumps(space)
    encrypted_aeskey = encrypt_message(pubKey, aeskey)
    encrypted_space = {
        "space": encrypt(nspace_str, aeskey),
        "aeskey": str(encrypted_aeskey)
    }
    space_size = convert_size( sys.getsizeof(space) )
    espace_size = convert_size( sys.getsizeof(encrypted_space) )

    print("      Size of nspace is: %s\n           └──encrypted: %s" % ( space_size, espace_size ) )
    return encrypted_space
    
def decrypt_space(encrypted_space, privKey):
    """
    Used as a caller to decrypt namespaces. 
    Takes dict with aeskey and space as encrypted string.
    
    It calls decrypt_message, to  
    decrypt the aeskey using your privKey. The decrypted 
    aeskey is then used to decrypt your namespace to json 
    for loads.

    Returns namespace as a dict
    """
    space = encrypted_space["space"]
    encrypted_aeskey = ast.literal_eval( encrypted_space["aeskey"] )

    aeskey = decrypt_message(privKey, encrypted_aeskey)
    nspace_string = decrypt(space, aeskey)
    nspace = json.loads(nspace_string)

    space_size = convert_size( sys.getsizeof(nspace) )
    espace_size = convert_size( sys.getsizeof(encrypted_space) )

    print("      Size of nspace is: %s\n          └──encrypted: %s" % ( space_size, espace_size ) )
    return nspace
