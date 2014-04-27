from Crypto.Cipher import AES
from Crypto import Random
import random

def board(boardList):
    random.shuffle(boardList)

    key = Random.new().read(AES.block_size)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    shuffledEncryptedList = []
    
    print boardList
    for i in xrange(len(boardList)):
        encryption = cipher.encrypt(str(boardList[i]))
        shuffledEncryptedList.append(encryption)
        
    return shuffledEncryptedList