from dataclasses import dataclass
from typing import Tuple, List
from enum import Enum


class FieldStyle(Enum):
    """Defines how templated fields are handled when interacting with existing embed fields.
    IGNORE: Templated fields are ignored. Existing fields remain. Default option.
    COMBINE: Templated fields are combined with existing fields.
    OVERRIDE: Templated fields override any existing fields.

    See https://github.com/robertwayne/dpymenus-book#field_overrides for more information.
    """

    IGNORE = 0
    COMBINE = 1
    OVERRIDE = 2


class FieldSort(Enum):
    """Defines how templated fields are sorted when using the FieldsStyle.COMBINE mode.
    FIRST: Templated fields are added before existing fields.
    LAST: Templated fields are added after existing fields. Default option.

    See https://github.com/robertwayne/dpymenus-book#field_overrides for more information.
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
    generally applied via strings or Dictionaries. See the examples on how templates should be defined."""

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
