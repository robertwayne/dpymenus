import asyncio
from typing import Dict, Optional, Union
from warnings import warn

from discord import Emoji, PartialEmoji
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import BaseMenu
from dpymenus.exceptions import ButtonsError, CallbackError


class ButtonMenu(BaseMenu):
    """Represents a button-based response menu.

    A ButtonMenu is a composable, dynamically generated object that contains state information for a user-interactable menu.
    It contains Page objects which represent new Menu states that call methods for validation and handling.

    Attributes:
        ctx: A reference to the command context.
        timeout: How long (in seconds) to wait before timing out.
        data: A dictionary containing variables to pass around menu functions.
    """

    def __init__(self, ctx: Context, timeout: int = 300, data: Optional[Dict] = None):
        super().__init__(ctx, timeout)
        self.data = data if data else {}

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, ' \
               f'active={self.active} page={self.page_index}, data={self.data}>'

    async def open(self):
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super().open()

        self.output = await self.ctx.send(embed=self.page)

        while self.active:
            await self._add_buttons()

            self.input = await self._get_reaction()
            await self._cleanup_reactions()

            await self.page.on_next(self)

    # Internal Methods
    async def _add_buttons(self, ) -> None:
        """Adds reactions to the message object based on what was passed into the page buttons."""
        for button in self.page.buttons:
            await self.output.add_reaction(button)

    async def _get_reaction(self) -> Union[Emoji, str]:
        """Collects a user reaction and places it into the input attribute. Returns an Emoji or Emoji name."""
        try:
            reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=self.timeout, check=lambda _, u: u == self.ctx.author)
        except asyncio.TimeoutError:
            await self._timeout()

        else:
            if isinstance(reaction.emoji, (Emoji, PartialEmoji)):
                return reaction.emoji.name
            return reaction.emoji

    async def _cleanup_reactions(self) -> None:
        """Removes all reactions from the output message object."""
        if isinstance(self.ctx.channel, GuildChannel):
            await self.output.clear_reactions()

    def _validate_buttons(self):
        """Ensures that a button menu was passed the appropriate amount of buttons."""
        for page in self.pages:
            if page.on_next is None:
                return

            if len(page.buttons) <= 1:
                raise ButtonsError('Your primary pages must have at least one button.')

            if self.page.on_fail:
                raise CallbackError('A ButtonMenu can not have an `on_fail` callback.')

            if len(self.page.buttons) > 5:
                warn('Adding more than 5 buttons to a message at once may result in throttling.')
