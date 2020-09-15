import logging
from typing import Any, Dict, Tuple

from dpymenus.base_menu import BaseMenu
from dpymenus.button_menu import ButtonMenu
from dpymenus.page import Page
from dpymenus.poll import Poll
from dpymenus.text_menu import TextMenu
from dpymenus.paginated_menu import PaginatedMenu

sessions: Dict[Tuple[int, int], Any]
sessions = dict()

logger = logging.getLogger('dpymenus')
logger.addHandler(logging.NullHandler())
