from typing import Dict, Optional

from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import BaseMenu


class TextMenu(BaseMenu):
    """
    Represents a text-based response menu.

    :param ctx: A reference to the command context.
    :param delay: How long to wait between deleting user messages (default 0.25).
    :param timeout: How long (in seconds) to wait before timing out.
    :param data: A dictionary containing variables to pass around menu functions.
    """

    def __init__(self, ctx: Context, delay: float = 0.250, timeout: int = 300, data: Optional[Dict] = None):
        self.delay = delay
        super().__init__(ctx, timeout)
        self.data = data if data else {}

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, ' \
               f'active={self.active} page={self.page_index}, data={self.data}>'

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super()._validate_pages()

        self.output = await self.ctx.send(embed=self.page)

        _first_iteration = True
        while self.active:
            if not _first_iteration and self.page.on_fail:
                return await self.page.on_fail()

            _first_iteration = False

            self.input = await self._get_input()
            await self._cleanup_input()

            if await self._is_cancelled():
                return

            await self.page.on_next(self)

    # Internal Methods
    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if isinstance(self.ctx.channel, GuildChannel):
            await self.input.delete(delay=self.delay)
