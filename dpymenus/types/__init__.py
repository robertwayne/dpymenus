from typing import Dict, TYPE_CHECKING, Tuple, TypeVar

from discord import Embed, Emoji, PartialEmoji

if TYPE_CHECKING:
    from dpymenus import Page
    from dpymenus import BaseMenu, TextMenu, ButtonMenu, PaginatedMenu, Poll

    SessionKey = int  # (session.owner.id)
    Menu = TypeVar('Menu', BaseMenu, TextMenu, ButtonMenu, PaginatedMenu, Poll)
    Button = TypeVar('Button', Emoji, PartialEmoji, str)
    PageType = TypeVar('PageType', Embed, Page, Dict)
