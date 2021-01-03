import json, requests, ast, datetime, sys, os
from .public_encryption import decrypt_message, generate_keys
from dateutil import parser
import math, base64, zlib
from .handlers import check_lspace, save_lspace
from .tools import convert_size
max_payload_size = 6186598.4

def register_namespace(alias, reg_code, pubKey=None, password=None):
    """
    Used for registering a new namespace. If no pubKey is provided
    one will be generated. The password is only used to encrypt
    the namespace locally
    """
    print( "    Registering namespace: %s" % (alias) )
    if pubKey == None:
        generate_keys()
        pubKey = os.environ["pubKey"]

    if check_lspace() == True:
        print("     Device already registred to a namespace")
        return False
    
    url='https://api.orman.xyz/register'
    payload = json.dumps({
        "action": "register",
        "alias": alias,
        "reg_code": reg_code,
        "pubKey": pubKey
    })
    r = requests.post(url, data=payload) 
    statusCode = r.status_code
    content = json.loads(r.content)

    if statusCode == 201:
        print("    Namespace registered succesfully")
        namespace = content["namespace"]
        namespace["privKey"] = os.environ["privKey"]
        save_lspace(namespace, password)
    else:
        print("     Something went wrong - %s" % (statusCode))
        quit()

    return statusCode

def get_token(alias, reg_code, privKey):
    """
    Used to retrieve an encrypted token from the orman api.
    The token will have been encrypted by the backed using the pubKey associated
    with the namespace alias provided in request. The privKey provided
    must match the pubKey for that namespace. It is used to decrypt the token, thus
    provid you are the owner of the namespace.

    The decrypted token can then be used to make administrative 
    actions on that namespace until it expires.

    Returns authToken as string.
    """
    data = json.dumps({
        "namespace": alias,
        "reg_code": reg_code
    })
    url="https://api.orman.xyz/auth"
    r = requests.post(url,data=data)  
    token_str = (r.__dict__['_content']).decode()
    r_token_obj = json.loads(token_str)
    token_cipher = ast.literal_eval( r_token_obj["token"] )
    token_obj = dict()
    token_obj = {
        "authToken": decrypt_message( privKey, token_cipher),
        "expiration_minutes": r_token_obj["expiration_minutes"],
        "expiration": str(datetime.datetime.now() + datetime.timedelta(minutes=r_token_obj["expiration_minutes"]))
    }
    expiration = token_obj["expiration"]
    expiration = parser.parse(expiration)
    if datetime.datetime.now() > expiration:
        print("Token has expired")
    else:
        c = expiration - datetime.datetime.now()
        valid_minutes = str(divmod(c.total_seconds(), 60)[0])
    return token_obj["authToken"]

def test_token(authToken):
    """
    Used to test the status of a authToken
    """
    url="https://api.orman.xyz/test"
    r = requests.get(url, headers={'authorizationToken': authToken}) 
    if r.status_code == 403:
        print("403")
        return False
    response = json.loads( r.content.decode() )
    return response

def sync_namespace(alias, reg_code, authToken, space=None, action=None):
    """
    Used to sync namespace to/from cloud.

    If no namespace is provided, a GET namespace request is assumed and 
    the requested namespace is returned as encrypted string. If a namespace 
    is provided then an UPDATE is assumed and the namespace will be saved to 
    the cloud. To delete a namespace, you must provide 'delete' as a string 
    instead of a namesapce onject
    """
    if space == None:
        action = 'get'
        print(" ACTION: GET")
    elif action == None:
        if 'aeskey' not in space:
            print("Space not encrypted")
            quit()
        action = 'update'
        print(" ACTION: UPDATE")
    elif action == 'delete':
        print(" ACTION: DELETE")
    url='https://api.orman.xyz/namespace'
    headers={'authorizationToken': authToken}
    data = json.dumps({'action': action, 'alias': alias, 'reg_code': reg_code, 'namespace': space})
    payload_size = sys.getsizeof(data)
    print("     Size of payload is: %s" % (convert_size(payload_size)))
    print("     Max payload is: %s" % (convert_size(max_payload_size)))
    if payload_size >= max_payload_size:
        print("     OVER MAX PAYLOAD: %s" % (convert_size(max_payload_size)))
        quit()
    r = requests.post(url, headers=headers, data=data) 
    print("     Request made")
    if r.status_code == 403:
        print("     Invalid registration code, exiting")
        quit()
    elif r.status_code == 406:
        print("     Namespace mismatch")
        quit()
    else:
        print("      └──statusCode:" + str(r.status_code) )
    return r
