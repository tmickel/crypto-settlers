from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto import Random
import base64

class Sign(object):
    def __init__(self):
        # Generate a random public/private key for this player
        # used for signing messages
        random_gen = Random.new().read
        self.key = RSA.generate(1024, random_gen)

    def sign(self, data):
        # Sign a SHA256 hash of the data using our key
        signer = PKCS1_v1_5.new(self.key)
        hashed = SHA256.new(data)
        return base64.b64encode(signer.sign(hashed))

    def verify(self, public_key, signature, data):
        # Verify the signature is valid for the public key, SHA256 hash of the data
        key = RSA.importKey(base64.b64decode(public_key))
        signer = PKCS1_v1_5.new(key)
        hashed = SHA256.new(data)
        return signer.verify(hashed, base64.b64decode(signature))

    def get_public_key(self):
        return base64.b64encode(self.key.publickey().exportKey('PEM'))
