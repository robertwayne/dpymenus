from typing import Dict, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from dpymenus import Session

sessions: Dict[Tuple[int, int], "Session"]
sessions = dict()
