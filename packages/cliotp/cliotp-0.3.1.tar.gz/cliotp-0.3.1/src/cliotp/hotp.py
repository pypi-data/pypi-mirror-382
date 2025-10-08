import hmac
from hashlib import sha1, sha256, sha512


class Hotp:
    def __init__(self, secret, code_digits=6, algorithm="sha1"):
        algorithm = self._get_hash_algorithm(algorithm)

        self.code_digits = code_digits
        self.secret = secret.bytes
        self.hash_algorithm = algorithm

    def generate_code(self, counter):
        self._set_counter(counter)
        hs = self.hmac_sha()
        snum = self.dynamic_truncation(hs)

        return self.compute_hotp(snum)

    def hmac_sha(self):
        digester = hmac.new(self.secret, self.counter, self.hash_algorithm)
        return digester.digest()

    def dynamic_truncation(self, hmac_result):
        last_byte = hmac_result[-1]

        offset = last_byte & 0xF

        return (
            (hmac_result[offset] & 0x7F) << 24
            | (hmac_result[offset + 1] & 0xFF) << 16
            | (hmac_result[offset + 2] & 0xFF) << 8
            | (hmac_result[offset + 3] & 0xFF)
        )

    def compute_hotp(self, snum):
        return snum % 10**self.code_digits

    def _set_counter(self, counter):
        self.counter = counter.to_bytes(8, byteorder="big")

    def _get_hash_algorithm(self, algorithm):
        match algorithm.lower():
            case "sha1":
                return sha1
            case "sha256":
                return sha256
            case "sha512":
                return sha512
            case _:
                raise Exception("Invalid Algorithm")
