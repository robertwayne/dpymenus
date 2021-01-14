from typing import Any, Dict

from dpymenus import Page


class Template:
    """Represents a Menu-style template used when constructing pages."""

    def __init__(self, options: Dict[str, Any]):
        self.options = options

    def to_page(self) -> "Page":
        return Page.convert_from(self.options.get("embed", None))

    def apply(self, page: "Page"):
        pass
