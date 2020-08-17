from typing import Callable, List, Optional, Union

from discord import Embed, Emoji, PartialEmoji


class Page:
    """Represents a single page inside a menu.

    Attributes
        :embed: A discord Embed object. Used in place of utilizing the Page as an Embed object itself.
    """
    embed: Embed
    index: int
    buttons: List[Union[str, Emoji, PartialEmoji]]
    on_next: Optional[Callable]
    on_fail: Optional[Callable]
    on_cancel: Optional[Callable]
    on_timeout: Optional[Callable]

    def __init__(self, embed: Embed):
        self.index = 0
        self.embed = embed
        self.buttons = []
        self.on_next = None
        self.on_fail = None
        self.on_cancel = None
        self.on_timeout = None

    def __str__(self):
        return f'<Page {self.embed.title}>'

    def __repr__(self):
        return f"Page(title={self.embed.title} {''.join([f'{k}={v}' for k, v in self.__dict__.items()])})"

    def set_buttons(self, buttons: List):
        self.buttons = buttons

        return self

    def set_event_next(self, func: Callable):
        self.on_next = func

        return self

    def set_event_fail(self, func: Callable):
        self.on_fail = func

        return self

    def set_event_cancel(self, func: Callable):
        self.on_cancel = func

        return self

    def set_event_timeout(self, func: Callable):
        self.on_timeout = func

        return self
