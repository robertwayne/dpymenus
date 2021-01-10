from typing import Dict, Tuple, Any
import logging

sessions: Dict[Tuple[int, int], Any]
sessions = dict()

logger = logging.getLogger("dpymenus")
logger.addHandler(logging.NullHandler())

from dpymenus.page import Page
from dpymenus.base_menu import BaseMenu
from dpymenus.text_menu import TextMenu
from dpymenus.button_menu import ButtonMenu
from dpymenus.paginated_menu import PaginatedMenu
from dpymenus.poll import Poll
