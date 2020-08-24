import asyncio
from typing import Dict, Optional, Union

from discord import Emoji, PartialEmoji, Reaction
from discord.abc import GuildChannel, User
from discord.ext.commands import Context

from dpymenus import BaseMenu


class ButtonMenu(BaseMenu):
    """
    Represents a button-based response menu.

    :param ctx: A reference to the command context.
    """

    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def __repr__(self):
        return f'ButtonMenu(pages={[p.__str__() for p in self.pages]}, page={self.page}, timeout={self.timeout}, data={self.data})'

    @property
    def data(self) -> Dict:
        return getattr(self, '_data', {})

    def set_data(self, data: Dict) -> 'ButtonMenu':
        """Sets a dictionary up for persistant state data. Returns itself for fluent-style chaining."""
        self._data = data

        return self

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super()._open()
        self._validate_buttons()

        while self.active:
            await self._add_buttons()

            self.input = await self._get_reaction()
            await self._cleanup_reactions()

            await self.page.on_next_event(self)

    # Internal Methods
    async def _add_buttons(self):
        """Adds reactions to the message object based on what was passed into the page buttons."""
        for button in self.page.buttons_list:
            await self.output.add_reaction(button)

    async def _get_reaction(self) -> Optional[Union[Emoji, str]]:
        """Collects a user reaction and places it into the input attribute. Returns a :py:class:`discord.Emoji` or string."""
        try:
            reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=self.timeout, check=self._check_reaction)

        except asyncio.TimeoutError:
            await self._timeout()

        else:
            if isinstance(reaction.emoji, (Emoji, PartialEmoji)):
                return reaction.emoji.name
            return reaction.emoji

    async def _cleanup_reactions(self):
        """Removes all reactions from the output message object."""
        if isinstance(self.output.channel, GuildChannel):
            await self.output.clear_reactions()

    def _check_reaction(self, r: Reaction, u: User) -> bool:
        """Returns true if the author is the person who reacted and the message ID's match. Checks the pages buttons."""
        if r.emoji in self.page.buttons or str(r.emoji) in self.page.buttons:
            return u == self.ctx.author and r.message.id == self.output.id
        return False
