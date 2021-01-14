from typing import Dict, Tuple, Any
import logging

sessions: Dict[Tuple[int, int], Any]
sessions = dict()

logger = logging.getLogger("dpymenus")
logger.addHandler(logging.NullHandler())

from dpymenus.page import Page
from dpymenus.menus.base_menu import BaseMenu
from dpymenus.menus.text_menu import TextMenu
from dpymenus.menus.button_menu import ButtonMenu
from dpymenus.menus.paginated_menu import PaginatedMenu
from dpymenus.menus.poll import Poll
