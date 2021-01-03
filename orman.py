from config import Config
from lib.handlers import load_space, save_lspace
from Crypto.PublicKey import RSA
import json, os, requests
from lib.public_encryption import encrypt_space, decrypt_space
from lib.api_actions import register_namespace, get_token, test_token, sync_namespace
from lib.tools import delete_local_namespace

class OrmanNameSpace(object):

    def __init__(self):
        # Config()
        self.alias = None
        self.pubKey = None
        self.privKey = None
        self.reg_code = None

    def save(self, space):
        return save_lspace(space)

    def init_space(self):
        space = load_space()
        self.privKey = space["privKey"]
        self.pubKey = space["pubKey"]
        self.alias = space["alias"]
        self.reg_code = space["reg_code"]
        self.space = space
        return space

    def ns(self, space=None):
        if (space) == None:
            return self.init_space()
        self.save(space)
        return space

    def register(self, alias, reg_code, password=None):
        return register_namespace(alias, reg_code, password=password)

    def encrypt(self, space):
        if self.pubKey == None:
            self.init_space()
        return encrypt_space(space, self.pubKey)

    def decrypt(self, space):
        if self.privKey == None:
            self.init_space()
        return decrypt_space(space, self.privKey)

    def token(self):
        if self.alias == None:
            self.init_space()
        token = get_token(
            self.alias, 
            self.reg_code, 
            self.privKey
        )
        os.environ["authToken"] = token
        return token

    def test(self, authToken):
        return test_token(authToken)

    def sync(self, space=None):
        enspace = space
        authToken = os.environ.get(
            "authToken",
            self.token()
        )
        if self.reg_code == None:
            self.init_space()
        if space:
            enspace = self.encrypt(space)
        r = sync_namespace(self.alias, self.reg_code, authToken, enspace)
        if space == None:
            encrypted_space = json.loads( r.content.decode() )
            space = self.decrypt(encrypted_space)
        return space

    def delete(self, alias, reg_code, authToken, confirm):
        response = sync_namespace(
            alias, 
            reg_code, 
            authToken, 
            confirm, 
            'delete'
        )
        delete_local_namespace()
        return response