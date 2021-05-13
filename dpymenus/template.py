from dataclasses import dataclass
from typing import Dict, Tuple, List, Union
from enum import Enum


class FieldStyle(Enum):
    """Defines how templated fields are handled when interacting with existing embed fields.

    See https://dpymenus.com/field_overrides.html for more information.
    """

    IGNORE = 0
    COMBINE = 1
    OVERRIDE = 2


class FieldSort(Enum):
    """Defines how templated fields are sorted when using the FieldsStyle.COMBINE mode.

    See https://dpymenus.com/field_overrides.html for more information.
    """

    FIRST = 0
    LAST = 1


# map Enum references so we can export them in a user-friendly way
IGNORE = FieldStyle.IGNORE
COMBINE = FieldStyle.COMBINE
OVERRIDE = FieldStyle.OVERRIDE

FIRST = FieldSort.FIRST
LAST = FieldSort.LAST


@dataclass
class Template:
    """Defines a Page template. Page templates contain most of the same options as Embed objects, but they are
    generally applied via strings or Dictionaries.

    See https://dpymenus.com/templates.html for more information.
    """

    title: str = None
    description: str = None
    color: str = None
    footer: Dict[str, str] = None
    image: str = None
    url: str = None
    thumbnail: str = None
    author: Dict[str, str] = None
    fields: List[Dict[str, Union[str, bool]]] = None
    field_style: FieldStyle = FieldStyle.IGNORE
    field_sort: FieldSort = FieldSort.LAST
