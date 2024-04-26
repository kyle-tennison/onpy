"""Manages OnShape credentials"""

from onpy.util.exceptions import PyshapeAuthError

import re
import os
import json
from loguru import logger


class CredentialManager:
    """Manages token retrieval and credential storing"""

    credential_path = os.path.expanduser(f"~/.onpy/config.json")

    @staticmethod
    def is_secret_key(token: str | None) -> bool:
        """Checks if dev secret key regex matches expected pattern

        Args:
            token: The token to check

        Returns:
            True if regex matches, False otherwise
        """

        if not token:
            return False

        return len(token) == 48

    @staticmethod
    def is_access_key(token: str | None) -> bool:
        """Checks if dev access key regex matches expected pattern

        Args:
            token: The token to check

        Returns:
            True if regex matches, False otherwise
        """

        if not token:
            return False

        return len(token) == 24

    @staticmethod
    def fetch_dev_tokens() -> tuple[str, str] | None:
        """Fetches dev secret and access tokens from file or env var

        Returns:
            A tuple of the (access_key, secret_key), or None if nothing is found
        """

        dev_secret = os.environ.get("ONSHAPE_DEV_SECRET")
        dev_access = os.environ.get("ONSHAPE_DEV_ACCESS")

        # look in file if no env var set
        if not dev_secret or not dev_access:

            if not os.path.exists(CredentialManager.credential_path):
                return None

            with open(CredentialManager.credential_path, "r") as f:
                data = json.load(f)
                dev_secret = str(data["dev_secret"])
                dev_access = str(data["dev_access"])

        if not CredentialManager.is_access_key(dev_access):
            raise PyshapeAuthError("Dev access key does not follow expected pattern")
        if not CredentialManager.is_secret_key(dev_secret):
            raise PyshapeAuthError("Dev secret key does not follow expected pattern")

        return (dev_access, dev_secret)

    @staticmethod
    def configure_file(access_token: str, secret_token: str) -> None:
        """Creates a configuration file at ~/.onpy/config.json

        Args:
            access_token: The access token/key from OnShape dev portal
            secret_token: The secret token/key from OnShape dev portal
        """

        # verify before adding
        if not CredentialManager.is_access_key(access_token):
            raise PyshapeAuthError(
                f"Cannot add token {access_token} to credentials file. "
                "Not a valid access key."
            )
        if not CredentialManager.is_secret_key(secret_token):
            raise PyshapeAuthError(
                f"Cannot add token {secret_token} to credentials file. "
                "Not a valid secret key."
            )

        os.makedirs(os.path.dirname(CredentialManager.credential_path), exist_ok=True)

        with open(CredentialManager.credential_path, "w") as f:
            contents = {"dev_access": access_token, "dev_secret": secret_token}
            json.dump(contents, f)

    @staticmethod
    def fetch_or_prompt() -> tuple[str, str]:
        """Fetches the dev and secret tokens if available, prompts user
        through CLI otherwise.

        Returns:
            A tuple of the (access_key, secret_key)
        """

        tokens = CredentialManager.fetch_dev_tokens()
        if tokens:
            return tokens

        print(
            "\nOnPy needs your OnShape credentials. \n"
            "navagate to https://dev-portal.onshape.com/keys and generate a pair of "
            "access & secret keys. Paste them here when prompted:\n"
        )

        while True:

            secret_key = input("secret key: ")

            if not CredentialManager.is_secret_key(secret_key):
                logger.error(
                    "the key you entered does not match the expected pattern of a secret key. please try again."
                )
                continue

            access_key = input("access key: ")

            if not CredentialManager.is_access_key(access_key):
                logger.error(
                    "the key you entered does not match the expected pattern of a access key. please try again."
                )
                continue

            break

        CredentialManager.configure_file(access_key, secret_key)
        tokens = CredentialManager.fetch_dev_tokens()
        assert tokens is not None
        return tokens
