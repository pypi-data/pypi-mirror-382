__author__ = "BSC Global"
__version__ = "0.1.1"

import warnings
from urllib.parse import urlsplit

import keyring.backend
import keyring.credentials
from keyring.compat import properties

from .plugin import CredentialProvider


class QerentKeyringBackend(keyring.backend.KeyringBackend):
    def __init__(self):
        self._cache = {}

    @properties.classproperty
    def priority(self) -> float:
        return 9.9

    def get_credential(
        self, service: str, username: str | None
    ) -> keyring.credentials.Credential | None:
        try:
            parsed = urlsplit(service)
        except Exception as e:
            warnings.warn(str(e))
            return None

        netloc = parsed.netloc.rpartition("@")[-1]

        if netloc is None or not netloc.endswith("distribution.qerent.ai"):
            return None

        provider = CredentialProvider()
        username, password = provider.get_credentials(service)

        if username and password:
            self._cache[service, username] = password
            return keyring.credentials.SimpleCredential(username, password)

    def get_password(self, service: str, username: str) -> str | None:
        password = self._cache.get((service, username), None)
        if password is not None:
            return password

        creds = self.get_credential(service, None)

        if creds and username == creds.username:
            return creds.password

        return None

    def set_password(self, service: str, username: str, password: str) -> None:
        # Defer setting a password to the next backend
        raise NotImplementedError()

    def delete_password(self, service: str, username: str) -> None:
        # Defer deleting a password to the next backend
        raise NotImplementedError()
