import os
import binascii

def genkey():
    K = os.urandom(16)
    iv = os.urandom(16)
    with open("K.txt", "wb") as K_file:
        K_file.write(binascii.hexlify(K)[0:16])
    with open("iv.txt", "wb") as iv_file:
        iv_file.write(binascii.hexlify(iv)[0:16])


# if __name__ == '__main__':
#     genkey()