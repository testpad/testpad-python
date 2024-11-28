from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    id: str
    name: str


@dataclass(frozen=True)
class Script:
    id: str
    number: int
    name: str
