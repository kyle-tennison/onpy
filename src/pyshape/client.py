"""Entry point to this library"""

from pyshape.util.credentials import CredentialManager

from loguru import logger
class Client:
    """Handles project management, authentication, and other related items"""

    def __init__(self) -> None:

        print("hi")
        
        self._credentials = CredentialManager.fetch_or_prompt()
        logger.info("logged into onshape")
