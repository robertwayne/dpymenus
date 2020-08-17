from typing import Dict

from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import BaseMenu


class TextMenu(BaseMenu):
    """
    Represents a text-based response menu.

    :param ctx: A reference to the command context.
    """
    delay: float
    data: Dict

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.delay = 0.250
        self.data = {}

    def __repr__(self):
        return f'TextMenu(pages={[p.__str__() for p in self.pages]}, page={self.page}, timeout={self.timeout}, data={self.data})'

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super()._open()

        first_iter = True
        while self.active:
            if not first_iter and self.page.on_fail:
                return await self.page.on_fail()

            first_iter = False

            self.input = await self._get_input()

            if self.input:
                await self._cleanup_input()

                if self._is_cancelled():
                    return await self.cancel()

                await self.page.on_next(self)

    def set_delay(self, delay: float) -> 'TextMenu':
        """Sets the delay on when a users message will be deleted in guild channeels. Returns itself for fluent-style chaining."""
        self.delay = delay

        return self

    def set_data(self, data: Dict) -> 'TextMenu':
        """Sets a dictionary up for persistant state data. Returns itself for fluent-style chaining."""
        self.data = data

        return self

    # Internal Methods
    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if isinstance(self.output.channel, GuildChannel):
            await self.input.delete(delay=self.delay)
