from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dpymenus import Session
    from dpymenus.types import SessionKey


sessions: ["SessionKey", "Session"] = dict()
