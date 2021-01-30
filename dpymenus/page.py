from typing import Any, Callable, Dict, List, TYPE_CHECKING, Union

from discord import Embed

if TYPE_CHECKING:
    from dpymenus import Template


class Page(Embed):
    """Represents a single page inside a menu."""

    __slots__ = (
        *Embed.__slots__,
        "_index",
        "_buttons_list",
        "_on_next_event",
        "_on_fail_event",
        "_on_cancel_event",
        "_on_timeout_event",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return (
            f"Page(title={self.title} "
            f"{''.join([f'{k}={v}' for k, v in {j: getattr(self, j) for j in self.__slots__}])})"
        )

    def __str__(self):
        return f"Page {self.index} {self.title}"

    @property
    def index(self) -> int:
        return getattr(self, "_index", 0)

    @index.setter
    def index(self, i: int):
        self._index = i

    @property
    def buttons_list(self) -> List:
        return getattr(self, "_buttons_list", [])

    def buttons(self, buttons: List) -> "Page":
        """Generates reaction buttons when the page is displayed. Returns itself for fluent-style chaining."""
        self._buttons_list = buttons

        return self

    @property
    def on_next_event(self) -> Callable:
        return getattr(self, "_on_next_event", None)

    def on_next(self, func: Callable) -> "Page":
        """Sets the function that will be called when the `next` event runs. Returns itself for fluent-style chaining."""
        self._on_next_event = func

        return self

    @property
    def on_fail_event(self) -> Callable:
        return getattr(self, "_on_fail_event", None)

    def on_fail(self, func: Callable) -> "Page":
        """Sets the function that will be called when the `fail` event runs. Returns itself for fluent-style chaining."""
        self._on_fail_event = func

        return self

    @property
    def on_cancel_event(self) -> Callable:
        return getattr(self, "_on_cancel_event", None)

    def on_cancel(self, func: Callable) -> "Page":
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style chaining."""
        self._on_cancel_event = func

        return self

    @property
    def on_timeout_event(self) -> Callable:
        return getattr(self, "_on_timeout_event", None)

    def on_timeout(self, func: Callable) -> "Page":
        """Sets the function that will be called when the `timeout` event runs. Returns itself for fluent-style chaining."""
        self._on_timeout_event = func

        return self

    def as_safe_embed(self) -> "Page":
        """Returns a page stripped of Callables and Page-specific properties so we can send it as a standard Embed."""
        safe_embed = self.to_dict()
        return Embed.from_dict(safe_embed)

    @staticmethod
    def convert_from(other: Union[Dict[str, Any], Embed]) -> "Page":
        """Returns a Page object from an Embed object or valid dictionary."""
        if type(other) == Embed:
            return Page.from_dict(other.to_dict())
        else:
            return Page.from_dict(other)

    def apply_template(self, template: "Template"):
        if self.title is None:
            self.title = template.set("title")

        if self.color is None:
            self.color = template.set("color")
