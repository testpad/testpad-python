from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass
class Company:
    name: str


@dataclass
class ApiKey:
    number: int
    label: str = Optional[str]
    expires: Optional[datetime] = None


@dataclass
class Project:
    id: int
    name: str
    description: str
    created: datetime


@dataclass
class Note:
    type: str  # will always be 'note'
    id: str
    name: str


@dataclass
class Test:
    id: int
    text: str
    indent: int
    # Tags and Notes will not be present in the response if no values are set
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    # Script ID is not returned from some endpoints
    script_id: int = None


@dataclass
class TestResult:
    result: str
    passed: bool = None
    comment: str = None
    issue: str = None

    def __post_init__(self):
        self.passed = self.result == "pass"


@dataclass
class Progress:
    total: int
    fail: int
    block: int
    query: int
    summary: str
    passed: int = None
    """ The data returned includes 'pass' however this is a Python keyword so it is transformed here """

    @classmethod
    def from_api(cls, data: dict):
        return cls(passed=data.pop("pass", 0), **data)


@dataclass
class Run:
    id: int

    headers: dict[str, str]
    """
    Additional context for the test run, for example,

     "headers": {
        "build": "1.1.0",
        "weather": "fair",
    }
    """

    results: dict[str, TestResult]
    """
    Results are specified as a dictionary of test_id and result, for example:

    "results": {
        "1": {
            "result": "fail",
            "comment": "some explanation"
        }
    }
    """
    # these value are optional:
    progress: Progress = None
    created: str = None
    state: str = None
    label: str = None
    assignee: str = None

    def __post_init__(self):
        self.results = {key: TestResult(**value) for key, value in self.results.items()}


@dataclass
class Script:
    type: str  # will always be 'script'
    id: int
    name: str
    created: datetime
    archived: bool = False
    progress: Progress = None
    """ The progress summary of this test script - optional,
        only returned when requested using the "progress" URL parameter """
    fields: List[Dict[str, Any]] = None
    """ This can be filtered out by the URL parameters """
    description: str = None
    """ Scripts do not require a description, this is optional """
    comments: str = None
    """ Scripts do not require report comments, this is optional """
    tests: List[Test] = None
    """ Tests are included in script endpoints by default, and folder endpoints when requested """
    runs: List[Run] = None
    """ Runs are included in script endpoints by default, and folder endpoints when requested """

    def __post_init__(self):
        if self.tests is not None:
            self.tests = [Test(**t) for t in self.tests]
        if self.runs is not None:
            self.runs = [Run(**r) for r in self.runs]
        if self.progress is not None:
            self.progress = Progress.from_api(self.progress)


@dataclass
class Folder:
    type: str  # will always be 'folder'
    id: str
    name: str
    contents: list[Union["Folder", Script, Note]]
