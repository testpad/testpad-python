from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass(frozen=True)
class Company:
    name: str


@dataclass(frozen=True)
class ApiKey:
    id: str
    number: int
    label: str = Optional[str]
    expires: Optional[datetime] = None


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    description: str
    created: datetime


@dataclass(frozen=True)
class Note:
    type: str  # will always be 'note'
    id: str
    name: str


@dataclass(frozen=True)
class Test:
    type: str  # will always be 'test'
    id: int
    script_id: int
    text: str
    indent: int
    tags: Optional[List[str]]
    notes: Optional[str]


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class Folder:
    type: str  # will always be 'folder'
    id: str
    name: str
    contents: list[Union["Folder", Script, Note]]


@dataclass(frozen=True)
class Run:
    type: str  # will always be 'run'
    id: int
    script_id: int
