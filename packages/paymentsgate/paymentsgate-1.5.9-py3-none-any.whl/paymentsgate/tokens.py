from dataclasses import dataclass
from jwt import JWT
import time


@dataclass
class AccessToken:
    token: str
    expiredAt: int

    def __init__(self, token):
        self.token = token
        jwdInstance = JWT()
        parsed = jwdInstance.decode(token, do_verify=False, do_time_check=False)
        self.expiredAt = int(parsed["exp"])

    @property
    def is_expired(self):
        if self.expiredAt:
            return int(time.time()) >= self.expiredAt
        return True

    def __str__(self) -> str:
        return self.token


@dataclass
class RefreshToken:
    token: str
    expiredAt: int

    def __init__(self, token, expiredAt):
        self.token = token
        self.expiredAt = expiredAt

    @property
    def is_expired(self):
        if self.expiredAt:
            return int(time.time()) >= self.expiredAt
        return True

    def __str__(self) -> str:
        return self.token
