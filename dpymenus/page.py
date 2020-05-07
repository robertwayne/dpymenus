from discord import Embed


class Page(Embed):
    """Represents a single page inside a menu. Subclasses the discord.py Embed class.

    Attributes:
        func: Reference to a Callable.
        buttons: A list of button objects.
    """

    def __init__(self, **kwargs):
        self.func = kwargs.get('func', None)
        self.buttons = kwargs.get('buttons', None)
        super().__init__(**kwargs)

    def __str__(self):
        return f'<Page {self.title}>'

    def __repr__(self):
        return f'Page(title={self.title} func={self.func})'
