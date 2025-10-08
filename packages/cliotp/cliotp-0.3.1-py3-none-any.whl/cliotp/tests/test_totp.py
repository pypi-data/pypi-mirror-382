import unittest

from cliotp.secret import Secret
from cliotp.totp import Totp


# https://datatracker.ietf.org/doc/html/rfc6238
# Expected values from Appendix B
class TotpTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = self.pad_secret("12345678901234567890")
        self.secret_256 = self.pad_secret("12345678901234567890", 32)
        self.secret_512 = self.pad_secret("12345678901234567890", 64)

        self.times = [
            59,
            1111111109,
            1111111111,
            1234567890,
            2000000000,
            20000000000,
        ]

    def pad_secret(self, secret, length=20):
        while len(secret) < length:
            secret += secret

        return Secret.from_string(secret[:length])

    def test_sha1(self):
        expected_codes = [
            94287082,
            7081804,
            14050471,
            89005924,
            69279037,
            65353130,
        ]

        totp = Totp(self.secret)

        codes = [totp.generate_code(t) for t in self.times]

        self.assertEqual(expected_codes, codes)

    def test_sha256(self):
        expected_codes = [
            46119246,
            68084774,
            67062674,
            91819424,
            90698825,
            77737706,
        ]

        totp = Totp(self.secret_256, algorithm="sha256")

        codes = [totp.generate_code(t) for t in self.times]

        self.assertEqual(expected_codes, codes)

    def test_sha512(self):
        expected_codes = [
            90693936,
            25091201,
            99943326,
            93441116,
            38618901,
            47863826,
        ]

        totp = Totp(self.secret_512, algorithm="sha512")

        codes = [totp.generate_code(t) for t in self.times]

        self.assertEqual(expected_codes, codes)
