from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Self, Union


@dataclass(frozen=True)
class Company:
    id: str
    name: str


@dataclass(frozen=True)
class ApiKey:
    id: str
    number: int
    label: str = Optional[str]
    expires: Optional[datetime] = None


@dataclass(frozen=True)
class Project:
    id: str
    number: int
    name: str
    description: str
    created: datetime


@dataclass(frozen=True)
class Note:
    type: str  # will always be 'note'
    id: str
    name: str


@dataclass(frozen=True)
class Script:
    type: str  # will always be 'script'
    id: str
    number: int
    name: str
    created: datetime


@dataclass(frozen=True)
class Folder:
    type: str  # will always be 'folder'
    id: str
    name: str
    contents: list[Union[Self, Script, Note]]


def parse_data(data: Dict[str, Any]) -> Union[Folder, Script, Note]:
    if data["type"] == "script":
        return Script(**data)
    elif data["type"] == "note":
        return Note(**data)
    elif data["type"] == "folder":
        # first coerce the contents list into correct types
        data["contents"] = [parse_data(cont) for cont in data["contents"]]
        return Folder(**data)
    raise ValueError(f"Unexpected type: {data['type']}")
