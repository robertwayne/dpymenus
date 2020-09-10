from typing import Callable, List, Optional, Union

from discord import Embed, Emoji, PartialEmoji

Callback = Optional[Callable]
ButtonList = List[Union[str, Emoji, PartialEmoji]]


class Page(Embed):
    """Represents a single page inside a menu.

    Attributes
        :embed: A discord Embed object. Used in place of utilizing the Page as an Embed object itself.
    """

    __slots__ = ('_index', '_buttons_list', '_on_next_event', '_on_fail_event', '_on_cancel_event', '_on_timeout_event')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"Page(title={self.title} " \
               f"{''.join([f'{k}={v}' for k, v in {j: getattr(self, j) for j in self.__slots__}])})"

    def __str__(self):
        return f'Page {self.index} {self.title}'

    @property
    def index(self) -> int:
        return getattr(self, '_index', 0)

    @index.setter
    def index(self, i: int):
        self._index = i

    @property
    def buttons_list(self) -> List:
        return getattr(self, '_buttons_list', [])

    def buttons(self, buttons: List) -> 'Page':
        """Generates reaction buttons when the page is displayed. Returns itself for fluent-style chaining."""
        self._buttons_list = buttons

        return self

    @property
    def on_next_event(self) -> Callable:
        return getattr(self, '_on_next_event', None)

    def on_next(self, func: Callable) -> 'Page':
        """Sets the function that will be called when the `next` event runs. Returns itself for fluent-style chaining."""
        self._on_next_event = func

        return self

    @property
    def on_fail_event(self) -> Callable:
        return getattr(self, '_on_fail_event', None)

    def on_fail(self, func: Callable) -> 'Page':
        """Sets the function that will be called when the `fail` event runs. Returns itself for fluent-style chaining."""
        self._on_fail_event = func

        return self

    @property
    def on_cancel_event(self) -> Callable:
        return getattr(self, '_on_cancel_event', None)

    def on_cancel(self, func: Callable) -> 'Page':
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style chaining."""
        self._on_cancel_event = func

        return self

    @property
    def on_timeout_event(self) -> Callable:
        return getattr(self, '_on_timeout_event', None)

    def on_timeout(self, func: Callable) -> 'Page':
        """Sets the function that will be called when the `timeout` event runs. Returns itself for fluent-style chaining."""
        self._on_timeout_event = func

        return self

    async def as_safe_embed(self) -> 'Page':
        """Returns a page stripped of Callables so we can send it as a standard Embed."""
        safe_embed = self
        safe_embed._on_next_event = None
        safe_embed._on_cancel_event = None
        safe_embed._on_fail_event = None
        safe_embed._on_timeout_event = None

        return self
