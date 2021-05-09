from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dpymenus import BaseMenu


class HookEvent(Enum):
    """Represents the menu events that can be hooked into.

    See https://dpymenus.com/hooks.html for more information.
    """

    OPEN = 0
    UPDATE = 1
    CLOSE = 2
    TIMEOUT = 3


class HookWhen(Enum):
    """Represents when to hook into a specified menu event.

    See https://dpymenus.com/hooks.html for more information.
    """

    BEFORE = 0
    AFTER = 1


# map Enum references so we can export them in a user-friendly way
OPEN = HookEvent.OPEN
UPDATE = HookEvent.UPDATE
CLOSE = HookEvent.CLOSE
TIMEOUT = HookEvent.TIMEOUT

BEFORE = HookWhen.BEFORE
AFTER = HookWhen.AFTER


async def call_hook(instance: 'BaseMenu', hook: str):
    """Checks if a menu instance contains a valid hook attribute and calls it asynchronously."""
    if fn := getattr(instance, hook, None):
        await fn()
