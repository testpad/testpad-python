from requests import Session

DEFAULT_USER_AGENT = "hello"


class Testpad:

    def __init__(self, session: Session = None, user_agent: str = None):
        self._session = session or Session()
        self._user_agent = user_agent or DEFAULT_USER_AGENT
