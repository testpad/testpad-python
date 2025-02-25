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
    script_id: int
    text: str
    indent: int
    # Tags and Notes will not be present in the response if no values are set
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


@dataclass
class Script:
    type: str  # will always be 'script'
    id: int
    name: str
    created: datetime
    fields: List[Dict[str, Any]]
    description: str = None
    """ Scripts do not require a description, this is optional """
    tests: List[Test] = None
    """ Tests are only included when requesting a script detail directly, not when retrieved in lists """

    def __post_init__(self):
        if self.tests is not None:
            self.tests = [Test(**t) for t in self.tests]


@dataclass
class Folder:
    type: str  # will always be 'folder'
    id: str
    name: str
    contents: list[Union["Folder", Script, Note]]


@dataclass
class TestResult:
    result: str
    passed: bool = None
    comment: str = None

    def __post_init__(self):
        self.passed = self.result == "pass"


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

    def __post_init__(self):
        self.results = {key: TestResult(**value) for key, value in self.results.items()}
