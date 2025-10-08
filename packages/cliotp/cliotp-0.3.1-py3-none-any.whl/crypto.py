import binascii
import os

from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

from config import PASSWORD_FILE


class Crypto:
    def __init__(self, model):
        self.model = model
        self.algorithm = AES(self._master_key())

    def encrypt(self, plain_text_code):
        encryptor = self._get_cipher().encryptor()
        cipher_text = encryptor.update(plain_text_code.encode())

        return cipher_text

    def decrypt(self, cipher_text):
        encryptor = self._get_cipher().decryptor()
        plain_text = encryptor.update(cipher_text)

        return plain_text.decode()

    @staticmethod
    def save_master_password(password, salt):
        with open(PASSWORD_FILE, "a") as file:
            master_password = Crypto._generate_master_password(
                password=password, salt=salt
            )
            file.write(master_password)

    @staticmethod
    def _generate_master_password(password, salt):
        kdf = Argon2id(
            salt=salt,
            length=16,
            iterations=1,
            lanes=4,
            memory_cost=2 * 1024 * 1024,
            ad=None,
            secret=None,
        )

        digest = kdf.derive(password.encode())
        return binascii.hexlify(digest).decode()

    @staticmethod
    def random_bytes(num=16):
        return os.urandom(num)

    def _master_key(self):
        with open(PASSWORD_FILE) as file:
            contents = file.read()
            password = contents.replace("\n", "")
            return password.encode()

    def _get_cipher(self):
        return Cipher(self.algorithm, mode=CBC(self.model.initialization_vector))
