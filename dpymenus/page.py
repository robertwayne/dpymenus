from typing import Callable, List, Optional, Union

from discord import Embed, Emoji, PartialEmoji

Callback = Optional[Callable]
ButtonList = List[Union[str, Emoji, PartialEmoji]]


class Page(Embed):
    """Represents a single page inside a menu.

    Attributes
        :embed: A discord Embed object. Used in place of utilizing the Page as an Embed object itself.
    """
    __slots__ = (*Embed.__slots__, 'embed', '_index', '_buttons', '_on_next', '_on_fail',
                 '_on_cancel', '_on_timeout')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # if embed is None:
        #     super().__init__(**kwargs)
        # else:
        #     # for k, v in embed.to_dict().items():
        #     #     self.__setattr__(f'_{k}', v)
        #     super().__init__(**embed.to_dict())

    def __repr__(self):
        return f"Page(title={self.title} " \
               f"{''.join([f'{k}={v}' for k, v in {j: getattr(self, j) for j in self.__slots__}])})"

    def __str__(self):
        return f'Page {self.index} {self.title}'

    @property
    def index(self):
        return getattr(self, '_index', 0)

    @index.setter
    def index(self, i: int):
        self._index = i

    @property
    def buttons(self):
        return getattr(self, '_buttons', [])

    @buttons.setter
    def buttons(self, button: Union[Emoji, PartialEmoji, str]):
        self._buttons.append(button)

    def set_buttons(self, buttons: List) -> 'Page':
        """Generates reaction buttons when the page is displayed. Returns itself for fluent-style chaining."""
        self._buttons = buttons

        return self

    @property
    def on_next(self):
        return getattr(self, '_on_next', None)

    def set_on_next(self, func: Callable) -> 'Page':
        """Sets the function that will be called when the `next` event runs. Returns itself for fluent-style chaining."""
        self._on_next = func

        return self

    @property
    def on_fail(self):
        return getattr(self, '_on_fail', None)

    def set_on_fail(self, func: Callable) -> 'Page':
        """Sets the function that will be called when the `fail` event runs. Returns itself for fluent-style chaining."""
        self._on_fail = func

        return self

    @property
    def on_cancel(self):
        return getattr(self, '_on_cancel', None)

    def set_on_cancel(self, func: Callable) -> 'Page':
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style chaining."""
        self._on_cancel = func

        return self

    @property
    def on_timeout(self):
        return getattr(self, '_on_timeout', None)

    def set_on_timeout(self, func: Callable) -> 'Page':
        """Sets the function that will be called when the `timeout` event runs. Returns itself for fluent-style chaining."""
        self._on_timeout = func

        return self
