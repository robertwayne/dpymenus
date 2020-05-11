from typing import Callable, List, Optional

from discord import Embed


class Page(Embed):
    """Represents a single page inside a menu. Subclasses the discord.py Embed class.

    Attributes:
        on_next: Reference to a Callable. Should be called manually.
        on_fail: Reference to a Callable. Called when user input fails.
        on_cancel: Reference to a Callable. Called when the cancel method is run.
        on_timeout: reference to a Callable. Called when a menu instance times out.
        buttons: A list of reaction Emoji objects or unicode strings.
    """

    def __init__(self, buttons: Optional[List] = None, on_next: Optional[Callable] = None, on_fail: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None, on_timeout: Optional[Callable] = None, **kwargs):
        self.buttons = buttons
        self.on_next = on_next
        self.on_fail = on_fail
        self.on_cancel = on_cancel
        self.on_timeout = on_timeout
        super().__init__(**kwargs)

    def __str__(self):
        return f'<Page {self.title}>'

    def __repr__(self):
        return f'Page(title={self.title} on_next={self.on_next}, on_fail={self.on_fail}, on_cancel={self.on_cancel}, on_timeout={self.on_timeout}, ' \
               f'buttons={self.buttons}, {super().__repr__()})'
