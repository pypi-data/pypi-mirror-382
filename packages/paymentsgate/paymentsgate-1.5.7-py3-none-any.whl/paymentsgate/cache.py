from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from paymentsgate.tokens import AccessToken, RefreshToken


class AbstractCache(ABC):
    """
    Abstract class for implementing custom caches used to cache the token
    """

    @abstractmethod
    def get_token(self, key: str) -> AccessToken | RefreshToken:
        """
        Fetch a token with the specified key from the cache
        """
        ...

    @abstractmethod
    def set_token(self, token: AccessToken | RefreshToken) -> None:
        """
        Save the token to the cache under the specified key
        """
        ...


@dataclass
class DefaultCache(AbstractCache):
    tokens: dict[str, AccessToken | RefreshToken] = field(
        default_factory=dict, init=False
    )

    def get_token(self, key: str) -> AccessToken | RefreshToken | None:
        return self.tokens.get(key)

    def set_token(self, token: AccessToken | RefreshToken) -> None:
        self.tokens[token.__class__.__name__] = token
