import unittest

from cliotp.hotp import Hotp
from cliotp.secret import Secret


# https://datatracker.ietf.org/doc/html/rfc4226
# Expected values from Appendix D
class HotpTestCase(unittest.TestCase):
    def setUp(self):
        secret = Secret.from_string("12345678901234567890")
        self.hotp = Hotp(secret)

    def test_hmac_sha(self):
        expected_hex = [
            "cc93cf18508d94934c64b65d8ba7667fb7cde4b0",
            "75a48a19d4cbe100644e8ac1397eea747a2d33ab",
            "0bacb7fa082fef30782211938bc1c5e70416ff44",
            "66c28227d03a2d5529262ff016a1e6ef76557ece",
            "a904c900a64b35909874b33e61c5938a8e15ed1c",
            "a37e783d7b7233c083d4f62926c7a25f238d0316",
            "bc9cd28561042c83f219324d3c607256c03272ae",
            "a4fb960c0bc06e1eabb804e5b397cdc4b45596fa",
            "1b3c89f65e6c9e883012052823443f048b4332db",
            "1637409809a679dc698207310c8c7fc07290d9e5",
        ]

        hex = []
        for i in range(10):
            self.hotp._set_counter(i)
            hex.append(self.hotp.hmac_sha().hex())

        self.assertEqual(expected_hex, hex)

    def test_dynamic_truncation(self):
        expected_values = [
            1284755224,
            1094287082,
            137359152,
            1726969429,
            1640338314,
            868254676,
            1918287922,
            82162583,
            673399871,
            645520489,
        ]

        values = []
        for i in range(10):
            self.hotp._set_counter(i)
            values.append(self.hotp.dynamic_truncation(self.hotp.hmac_sha()))

        self.assertEqual(expected_values, values)

    def test_generate_code(self):
        expected_codes = [
            755224,
            287082,
            359152,
            969429,
            338314,
            254676,
            287922,
            162583,
            399871,
            520489,
        ]

        codes = [self.hotp.generate_code(i) for i in range(10)]
        self.assertEqual(expected_codes, codes)
