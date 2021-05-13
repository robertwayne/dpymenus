from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from dpymenus import Session
    from dpymenus.types import SessionKey


sessions: Dict['SessionKey', 'Session'] = dict()
