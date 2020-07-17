import asyncio
from typing import List, Union

from discord import Embed, Emoji, Message, PartialEmoji
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import ButtonMenu, Page
from dpymenus.constants import GENERIC_BUTTONS


class PaginatedMenu(ButtonMenu):
    """
    Represents an paginated, button-based response menu.

    :param ctx: A reference to the command context.
    :param timeout: How long (in seconds) to wait before timing out.
    """

    def __init__(self, ctx: Context, timeout: int = 300):
        super().__init__(ctx, timeout)

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, ' \
               f'active={self.active} page={self.page_index}, data={self.data}>'

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super()._validate_pages()

        self.output = await self.ctx.send(embed=self.page)

        await self._add_buttons()

        while self.active:
            pending, done = set(), set()

            try:
                done, pending = await asyncio.wait([asyncio.create_task(self._get_reaction()), asyncio.create_task(self._get_reaction_remove())], return_when=asyncio.FIRST_COMPLETED)
            finally:
                for task in pending:
                    task.cancel()

                for future in done:
                    self.input = future.result()

                if isinstance(self.output.channel, GuildChannel):
                    await self.output.remove_reaction(self.input, self.ctx.author)

                await self.handle_transition()

        await self._cleanup_reactions()

    async def send_message(self, embed: Embed) -> Message:
        """
        Edits a message if the channel is in a Guild, otherwise sends it to the current channel.

        :param embed: A Discord :py:class:`~discord.Embed` object.
        """
        return await self.output.edit(embed=embed)

    async def _next(self):
        """Paginated version of :class:`~dpymenus.BaseMenu`s `next` method. Checks for end-of-the-list."""
        if self.page_index + 1 > len(self.pages) - 1:
            return

        self.page_index += 1
        self.page = self.pages[self.page_index]

        await self.send_message(self.page)

    async def _previous(self):
        """Paginated version of :class:`~dpymenus.BaseMenu`s `previous` method. Checks for start-of-the-list."""
        if self.page_index - 1 < 0:
            return

        self.page_index -= 1
        self.page = self.pages[self.page_index]

        await self.send_message(self.page)

    # Internal Methods
    async def _get_reaction_remove(self) -> Union[Emoji, str]:
        """Collects a user reaction and places it into the input attribute. Returns an Emoji or Emoji name."""
        try:
            reaction, user = await self.ctx.bot.wait_for('reaction_remove', timeout=self.timeout, check=lambda _, u: u == self.ctx.author)

        except asyncio.TimeoutError:
            await self._timeout()

        else:
            if isinstance(reaction.emoji, (Emoji, PartialEmoji)):
                return reaction.emoji.name
            return reaction.emoji

    async def _add_buttons(self):
        """Adds reactions to the message object based on what was passed into the page buttons."""
        for button in GENERIC_BUTTONS:
            await self.output.add_reaction(button)

    async def add_pages(self, embeds: List[Embed]):
        """Helper method to add a list of pre-instantiated pages to a menu."""
        for embed in embeds:
            self.pages.append(Page(embed=embed))

        self.page = self.pages[0]

    async def handle_transition(self):
        transition_map = {GENERIC_BUTTONS[0]: self._previous, GENERIC_BUTTONS[1]: self.cancel, GENERIC_BUTTONS[2]: self._next}
        await transition_map[self.input]()
