from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dpymenus import BaseMenu


async def call_hook(instance: 'BaseMenu', hook: str):
    if fn := getattr(instance, hook, None):
        await fn()
