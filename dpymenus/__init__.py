from typing import Dict, TypeVar

from discord import Embed

from dpymenus.base_menu import BaseMenu
from dpymenus.button_menu import ButtonMenu
from dpymenus.page import Page
from dpymenus.paginated_menu import PaginatedMenu
from dpymenus.poll import Poll
from dpymenus.text_menu import TextMenu

PageType = TypeVar('PageType', Embed, Page, Dict)
