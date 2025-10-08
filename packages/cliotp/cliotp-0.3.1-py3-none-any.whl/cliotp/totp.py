from datetime import datetime, timezone

from .hotp import Hotp


class Totp:
    def __init__(self, secret, algorithm="sha1", time_step=30, code_digits=8):
        self.hotp = Hotp(secret, code_digits=code_digits, algorithm=algorithm)
        self.time_step = time_step

    def generate_code(self, current_timestamp=None):
        current_timestamp = current_timestamp or int(
            datetime.now(tz=timezone.utc).timestamp()
        )

        t = int(current_timestamp / self.time_step)
        return self.hotp.generate_code(t)
