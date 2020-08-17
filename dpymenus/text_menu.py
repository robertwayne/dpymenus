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
        super()._validate_pages()

        if self._start_session() is False:
            return

        self.output = await self.destination.send(embed=self.page.embed)

        _first_iteration = True
        while self.active:
            if not _first_iteration and self.page.on_fail:
                return await self.page.on_fail()

            _first_iteration = False

            self.input = await self._get_input()

            if self.input:
                await self._cleanup_input()

                if self._is_cancelled():
                    return await self.cancel()

                await self.page.on_next(self)

    def set_delay(self, delay: float):
        """Sets the delay on when a users message will be deleted in guild channeels. Returns the menu instance to allow for fluent-style chaining."""
        self.delay = delay

        return self

    def set_data(self, data: Dict):
        """Sets a dictionary up for persistant state data. Returns the menu instance to allow for fluent-style chaining."""
        self.data = data

        return self

    # Internal Methods
    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if isinstance(self.output.channel, GuildChannel):
            await self.input.delete(delay=self.delay)
