from typing import Callable, List, Optional

from discord import Embed


class Page(Embed):
    """Represents a single page inside a menu. Subclasses the discord.py Embed class.

    Attributes:
        callback: Reference to a Callable.
        buttons: A list of button objects.
    """

    def __init__(self, callback: Optional[Callable] = None, buttons: List = None, **kwargs):
        self.callback = callback
        self.buttons = buttons
        super().__init__(**kwargs)

    def __str__(self):
        return f'<Page {self.title}>'

    def __repr__(self):
        return f'Page(title={self.title} callback={self.callback})'


class DynamicPage(Page):
    pass


class StaticPage(Page):
    pass
