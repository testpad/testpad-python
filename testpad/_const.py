import sys
from importlib.metadata import version

VERSION = str(version("testpad-python"))
_python_version = ".".join(str(v) for v in sys.version_info[:2])
_requests_version = str(version("requests"))
DEFAULT_USER_AGENT = (
    f"testpad-python [t{VERSION}::p{_python_version}::r{_requests_version}]"
)
TESTPAD_API = "https://api.testpad.com/api/v1/"
