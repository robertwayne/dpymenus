from typing import Callable, List, Optional

from discord import Embed


class Page(Embed):
    """Represents a single page inside a menu. Subclasses :py:class:`~discord.Embed`.

    Attributes
        :on_next: Reference to a Callable. Should be called manually.
        :on_fail: Reference to a Callable. Called when user input fails.
        :on_cancel: Reference to a Callable. Called when the cancel method is run.
        :on_timeout: reference to a Callable. Called when a menu instance times out.
        :embed: A discord Embed object. Used in place of utilizing the Page as an Embed object itself.
        :buttons: A list of reaction Emoji objects or unicode strings.
    """

    def __init__(self, buttons: Optional[List] = None, on_next: Optional[Callable] = None, on_fail: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None, on_timeout: Optional[Callable] = None, embed: Optional[Embed] = None, **kwargs):
        self.embed = embed
        self.buttons = buttons
        self.on_next = on_next
        self.on_fail = on_fail
        self.on_cancel = on_cancel
        self.on_timeout = on_timeout

        if embed is None:
            super().__init__(**kwargs)
        else:
            for k, v in embed.to_dict().items():
                self.__setattr__(f'_{k}', v)
            super().__init__(**embed.to_dict())

    def __str__(self):
        return f'<Page {self.title}>'

    def __repr__(self):
        return f'Page(title={self.title} on_next={self.on_next}, on_fail={self.on_fail}, on_cancel={self.on_cancel}, ' \
               f'on_timeout={self.on_timeout}, buttons={self.buttons}, embed={self.embed} {super().__repr__()})'
