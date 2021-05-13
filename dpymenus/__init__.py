"""
dpymenus -- Simplified menus for discord.py developers.
"""

__title__ = 'dpymenus'
__author__ = 'Rob Wagner <rob@robwagner.dev>'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020-2021 Rob Wagner'
__version__ = '2.0.0'

import logging

from .exceptions import PagesError, ButtonsError, EventError, SessionError
from .sessions import sessions
from .sessions.session import Session
from .hooks import HookWhen, HookEvent
from .template import Template, FieldSort, FieldStyle
from .page import Page
from .base_menu import BaseMenu
from .text_menu import TextMenu
from .button_menu import ButtonMenu
from .paginated_menu import PaginatedMenu
from .poll import Poll


logger = logging.getLogger('dpymenus')
logger.addHandler(logging.NullHandler())
