# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
import base64


BLOCK_SIZE = 16
PADDING = '\0'
pad_it = lambda s: s+(16 - len(s)%16)*PADDING


def encrypt(str, key, iv):
    generator = AES.new(key, AES.MODE_CFB, iv)
    crypt = generator.encrypt(pad_it(str).encode('utf-8'))
    en_str = base64.b64encode(crypt)
    return en_str

def decrypt(en_str, key, iv):
    generator = AES.new(key, AES.MODE_CFB, iv)
    en_str = base64.b64decode(en_str)
    de_crypt = generator.decrypt(en_str)
    de_str = de_crypt.rstrip(PADDING.encode('utf-8'))
    return de_str

# if __name__ == '__main__':
#     K = b'ce6eed64a11aeaa1'
#     iv = b'e3893026736d6161'
#     Str = "hello world!"
#     print("str:", Str)
#     print("encrypt:", encrypt(Str, K, iv))
#     print("decrypt:", decrypt(encrypt(Str, K, iv), K, iv).decode("utf-8"))