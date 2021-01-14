from typing import Any, Dict

from dpymenus import Page


class Template:
    """Represents a Menu-style template used when constructing pages."""

    def __init__(self, options: Dict[str, Any]):
        self.options = options

    def set(self, key: str) -> Any:
        return self.options.get(key, None)
