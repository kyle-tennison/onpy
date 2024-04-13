"""Manages OnShape credentials"""


from pyshape.util.exceptions import OnshapeAuthError

import re
import os
import json

class CredentialManager:
    """Manages token retrieval and credential storing"""

    credential_path = os.path.expanduser(f"~/.pyshape/config.json")

    @staticmethod
    def is_dev_secret_key(token: str | None) -> bool:
        """Checks if dev secret key regex matches expected pattern"""

        if not token:
            return False

        return bool(re.match(r'^[A-Z0-9]{24}$', token))

    @staticmethod
    def is_dev_access_key(token: str | None) -> bool:
        """Checks if dev access key regex matches expected pattern"""

        if not token:
            return False

        return bool(re.match(r'^[a-zA-Z0-9]{64}$', token))

    @staticmethod
    def fetch_dev_tokens() -> tuple[str, str]:
        """Fetches dev secret and access tokens from file or env var"""

        dev_secret = os.environ.get("ONSHAPE_DEV_SECRET")
        dev_access = os.environ.get("ONSHAPE_DEV_ACCESS")

        # look in file if no env var set
        if not dev_secret or not dev_access:

            if not os.path.exists(CredentialManager.credential_path):
                raise OnshapeAuthError("Missing credential file")
            
            with open(CredentialManager.credential_path, 'r') as f:
                data = json.load(f)
                dev_secret = str(data["dev_secret"])
                dev_access = str(data["dev_access"])

        if not CredentialManager.is_dev_access_key(dev_access):
            raise OnshapeAuthError("Dev access key does not follow expected pattern")
        if not CredentialManager.is_dev_secret_key(dev_secret):
            raise OnshapeAuthError("Dev secret key does not follow expected pattern")
        
        return (dev_access, dev_secret)
    
    @staticmethod
    def configure_file(access_token, secret_token) -> None:
        """Creates a configuration file at ~/.pyshape/config.json"""

        # verify before adding
        if not CredentialManager.is_dev_access_key(access_token):
            raise OnshapeAuthError(f"Cannot add token {access_token} to credentials file. "
                                    "Not a valid access key.")
        if not CredentialManager.is_dev_secret_key(secret_token):
            raise OnshapeAuthError(f"Cannot add token {secret_token} to credentials file. "
                                    "Not a valid secret key.")
        

        os.makedirs(CredentialManager.credential_path, exist_ok=True)

        with open(CredentialManager.credential_path, "w") as f:
            contents = {
                "dev_access" : access_token,
                "dev_secret": secret_token
                }
            json.dump(contents, f)
        
        