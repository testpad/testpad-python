import sys
from importlib.metadata import version

from requests import Session

from . import models

VERSION = str(version("testpad"))
_python_version = ".".join(str(v) for v in sys.version_info[:2])
_requests_version = str(version("requests"))

DEFAULT_USER_AGENT = (
    f"testpad-python [t{VERSION}::p{_python_version}::r{_requests_version}]"
)

TESTPAD_API = "https://api.testpad.com"


class Testpad:

    def __init__(
        self,
        token: str,
        *,
        api_url: str = TESTPAD_API,
        user_agent: str = DEFAULT_USER_AGENT,
        session: Session = None,
    ):
        """
        Required parameters:

        :param token:
            The API token made at https://testpad.com/ to access the API

        Optional parameters:

        :param api_url:
            The base API URL. The default is for live testpad.com, but you can switch this for testing and development
        :param user_agent:
            Override the default user agent used to send in requests
        :param session:
            Use this to override the default requests Session object
        """
        self._token = token
        self._base_url = api_url

        self._session = session or Session()

        # set default headers including auth
        self._session.headers.update(
            {
                "User-Agent": user_agent,
                "Authorization": f"Token {self._token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def whoami(self) -> models.User:
        pass
