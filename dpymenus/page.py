from typing import Callable, List, Optional

from discord import Embed


class Page(Embed):
    """Represents a single page inside a menu. Subclasses the discord.py Embed class.

    Attributes:
        on_next: Reference to a Callable.
        buttons: A list of reaction Emoji objects or unicode strings.
    """

    def __init__(self, on_next: Optional[Callable] = None, on_fail: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None, on_timeout: Optional[Callable] = None,
                 buttons: List = None, **kwargs):
        self.on_next = on_next
        self.on_fail = on_fail
        self.on_cancel = on_cancel
        self.on_timeout = on_timeout
        self.buttons = buttons
        super().__init__(**kwargs)

    def __str__(self):
        return f'<Page {self.title}>'

    def __repr__(self):
        return f'Page(title={self.title} on_next={self.on_next})'
