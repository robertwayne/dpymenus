from typing import Dict, Optional

from discord.ext.commands import Context

from dpymenus import BaseMenu


class TextMenu(BaseMenu):
    """Represents a text-based response menu.

    A TextMenu is a composable, dynamically generated object that contains state information for a user-interactable menu.
    It contains Page objects which represent new Menu states that call methods for validation and handling.

    Attributes:
        ctx: A reference to the command Context.
        timeout: How long (in seconds) to wait before timing out.
        state_fields: A dictionary containing dynamic state state_fields you wish to pass around the menu.
    """

    def __init__(self, ctx: Context, timeout: int = 300, state_fields: Optional[Dict] = None):
        super().__init__(ctx, timeout)
        self.state_fields = state_fields if state_fields else {}

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, ' \
               f'active={self.active} page={self.page}, state_fields={self.state_fields}>'

    async def open(self):
        """The entry point to a new TextMenu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super().open()

        self.output = await self.ctx.send(embed=self.pages[self.page])

        while self.active:

            self.input = await self._get_input()
            await self._cleanup_input()

            if await self._is_cancelled():
                return

            await self.pages[self.page].callback(self)
