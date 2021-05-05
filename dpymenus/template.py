from dataclasses import dataclass
from typing import Tuple, List
from enum import Enum


class FieldStyle(Enum):
    IGNORE = 2
    COMBINE = 1
    OVERRIDE = 0


class FieldSort(Enum):
    FIRST = 1
    LAST = 0


@dataclass
class Template:
    title: str = None
    description: str = None
    color: str = None
    footer: dict = None
    image: str = None
    url: str = None
    thumbnail: str = None
    author: dict = None
    fields: List[Tuple[str, str, bool]] = None
    field_style: FieldStyle = FieldStyle.IGNORE
    field_sort: FieldSort = FieldSort.LAST
