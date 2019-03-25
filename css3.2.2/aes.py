from Crypto.Cipher import AES
from binascii import b2a_base64, a2b_base64


class Prpcrypt(object):
    def __init__(self, key):
        self.mode = AES.MODE_CBC
        self.key = self.pad_key(key)

    def pad(self, text):
        text = bytes(text, encoding="utf8")
        while len(text) % 16 != 0:
            text += b'\0'
        return text

    def pad_key(self, key):
        key = bytes(key, encoding="utf8")
        while len(key) % 16 != 0:
            key += b'\0'
        return key

    def encrypt(self, text):
        texts = self.pad(text)
        aes = AES.new(self.key, self.mode, self.key)
        res = aes.encrypt(texts)
        return str(b2a_base64(res), encoding="utf-8")

    def decrypt(self, text):
        texts = a2b_base64(self.pad(text))
        aes = AES.new(self.key, self.mode, self.key)
        res = str(aes.decrypt(texts), encoding="utf8")
        return res


if __name__ == "__main__":
    key = "jcjjzgzzgsgss"
    text = "你好！Python"
    a = Prpcrypt(key).encrypt(text)
    b = Prpcrypt(key).decrypt(a)
    print(a)
    print(b)
