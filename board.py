from Crypto.Cipher import AES
from Crypto import Random
import random
import base64

def board_shuffle_and_encrypt(boardList):
    """Shuffle and encrypt the given board list and return the shuffled,
       encrypted version, along with the IV and key used to encrypt."""
    bl_copy = list(boardList)
    random.shuffle(bl_copy)
    key = Random.new().read(AES.block_size)
    iv = Random.new().read(AES.block_size)
    shuffledEncryptedList = []
    for i in xrange(len(bl_copy)):
        cipher = AES.new(key, AES.MODE_CFB, iv)
        encryption = cipher.encrypt(str(bl_copy[i]))
        shuffledEncryptedList.append(base64.b64encode(encryption))
    return (shuffledEncryptedList, base64.b64encode(key), base64.b64encode(iv))

def board_decrypt(boardList, key, iv):
    """Decrypt a board list given the list, a key, and IV as given
       from board_shuffle_and_encrypt."""
    decrypted_list = []
    for i in xrange(len(boardList)):
      cipher = AES.new(base64.b64decode(key), AES.MODE_CFB, base64.b64decode(iv))
      decrypted = cipher.decrypt(base64.b64decode(boardList[i]))
      decrypted_list.append(decrypted)
    return decrypted_list