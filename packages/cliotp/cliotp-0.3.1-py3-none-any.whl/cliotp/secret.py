# Similar to https://github.com/hectorm/otpauth/blob/a1140673e4abc86c81803011b4659ad1c5cff85d/src/secret.js
# Secrets are usually Base32 encoded: https://github.com/google/google-authenticator/wiki/Key-Uri-Format#secret
import base64


class Secret:
    def __init__(self, bytes):
        self.bytes = bytes

    @classmethod
    def from_string(self, secret):
        return self(secret.encode())

    @classmethod
    def from_base32(self, secret):
        return self(base64.b32decode(secret))
