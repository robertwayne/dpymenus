from typing import Dict, TypeVar

from discord import Embed, Emoji, PartialEmoji

from dpymenus import Page

PageType = TypeVar('PageType', Embed, Page, Dict)
Button = TypeVar('Button', Emoji, PartialEmoji, str)
