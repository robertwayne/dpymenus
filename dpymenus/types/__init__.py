from typing import Dict, TYPE_CHECKING, Tuple, TypeVar

from discord import Embed, Emoji, PartialEmoji

if TYPE_CHECKING:
    from dpymenus import Page
    from dpymenus import TextMenu, ButtonMenu, PaginatedMenu, Poll

    SessionKey = Tuple[int, int]  # (session.owner.id, session.channel.id)
    Menu = TypeVar("Menu", TextMenu, ButtonMenu, PaginatedMenu, Poll)
    Button = TypeVar("Button", Emoji, PartialEmoji, str)
    PageType = TypeVar("PageType", Embed, Page, Dict)
