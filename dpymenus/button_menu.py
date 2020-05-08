import asyncio
from typing import Dict, Optional

from discord import Emoji, Message, PartialEmoji
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import BaseMenu
from dpymenus.exceptions import NoButtonsError


class ButtonMenu(BaseMenu):
    """Represents a button-based response menu.

    A ButtonMenu is a composable, dynamically generated object that contains state information for a user-interactable menu.
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

    async def run(self):
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super().run()

        self.output = await self.ctx.send(embed=self.pages[self.page])

        while self.active:
            await self.add_buttons()

            self.input = await self._get_reaction()
            await self._cleanup_reactions()

            await self.pages[self.page].callback(self)

    async def close(self):
        """Closes the active Menu instance."""
        await self._cleanup_reactions()
        self.active = False

    async def add_buttons(self, ) -> None:
        for button in self.pages[self.page].buttons:
            await self.output.add_reaction(button)

    async def _get_reaction(self) -> Message:
        """Collects a user reaction and places it into the input attribute."""
        try:
            reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=self.timeout, check=lambda _, u: u == self.ctx.author)
        except asyncio.TimeoutError:
            await self._timeout()

        else:
            if isinstance(reaction.emoji, (Emoji, PartialEmoji)):
                return reaction.emoji.name
            return reaction.emoji

    async def _cleanup_reactions(self) -> None:
        if isinstance(self.ctx.channel, GuildChannel):
            await self.output.clear_reactions()

    def _validate_buttons(self):
        for page in self.pages:
            if page.callback is None:
                return

            if len(page.buttons) <= 1:
                raise NoButtonsError('Your primary pages must have at least one button.')
