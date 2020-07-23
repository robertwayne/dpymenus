import asyncio
from typing import List, Optional, Union

from discord import Embed, Emoji, Message, PartialEmoji, Reaction
from discord.abc import GuildChannel, User
from discord.ext.commands import Context

from dpymenus import ButtonMenu, Page
from dpymenus.constants import GENERIC_BUTTONS


class PaginatedMenu(ButtonMenu):
    """
    Represents an paginated, button-based response menu.

    :param ctx: A reference to the command context.
    :param page_numbers: Whether embeds should display the current/max page numbers in the footer.
    :param timeout: How long (in seconds) to wait before timing out.
    :param on_cancel: An Embed that displays when the cancel button is pressed.
    :param on_timeout: An Embed that displays when the menu raises an asyncio.TimeoutError.
    """

    def __init__(self, ctx: Context, page_numbers: bool = False, timeout: int = 300,
                 on_cancel: Optional[Embed] = None, on_timeout: Optional[Embed] = None):
        super().__init__(ctx, timeout)
        self.page_numbers = page_numbers
        self.on_cancel = on_cancel
        self.on_timeout = on_timeout

    def __repr__(self):
        return f'PaginatedMenu(pages={[p.__str__() for p in self.pages]}, page_numbers={self.page_numbers}, timeout={self.timeout}, ' \
               f'active={self.active} page={self.page_index}, on_timeout={self.on_timeout}, on_cancel={self.on_cancel})'

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super()._validate_pages()

        if await self._start_session() is False:
            return

        self.output = await self.ctx.send(embed=self.page)

        await self._add_buttons()

        while self.active:
            done, pending = await asyncio.wait([asyncio.create_task(self._get_reaction()),
                                                asyncio.create_task(self._get_reaction_remove())],
                                               return_when=asyncio.FIRST_COMPLETED,
                                               timeout=self.timeout)

            # if we both tasks are still pending, we force a timeout by manually calling cleanup methods
            if len(pending) == 2:
                await self._timeout()

            else:
                for future in done:
                    self.input = future.result()

                if isinstance(self.output.channel, GuildChannel):
                    await self.output.remove_reaction(self.input, self.ctx.author)

                await self._handle_transition()

            for task in pending:
                task.cancel()

        await self._cleanup_reactions()

    async def send_message(self, embed: Embed) -> Message:
        """
        Edits the menu output message. We override the :class:`~dpymenus.BaseMenu` implementation because
        we always want to edit, even in a DM channel type.

        :param embed: A Discord :py:class:`~discord.Embed` object.
        """
        return await self.output.edit(embed=embed)

    async def add_pages(self, embeds: List[Embed]):
        """Helper method to add a list of pre-instantiated pages to a menu."""
        for i, embed in enumerate(embeds):
            if self.page_numbers:
                embed.set_footer(text=f'{i + 1}/{len(embeds)}')

            self.pages.append(Page(embed=embed))

        self.page = self.pages[0]

    # Internal Methods
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

    async def _get_reaction(self) -> Union[Emoji, str]:
        """Collects a user reaction and places it into the input attribute. Returns an Emoji or Emoji name."""
        reaction, user = await self.ctx.bot.wait_for('reaction_add',
                                                     check=self._check_reaction)

        if isinstance(reaction.emoji, (Emoji, PartialEmoji)):
            return reaction.emoji.name
        return reaction.emoji

    async def _get_reaction_remove(self) -> Union[Emoji, str]:
        """Collects a user reaction and places it into the input attribute. Returns an Emoji or Emoji name."""

        reaction, user = await self.ctx.bot.wait_for('reaction_remove',
                                                     check=self._check_reaction)

        if isinstance(reaction.emoji, (Emoji, PartialEmoji)):
            return reaction.emoji.name
        return reaction.emoji

    def _check_reaction(self, r: Reaction, u: User) -> bool:
        """Returns true if the author is the person who reacted and the message ID's match. Checks the generic buttons."""
        if r.emoji in GENERIC_BUTTONS:
            return u == self.ctx.author and r.message.id == self.output.id
        return False

    async def _add_buttons(self):
        """Adds reactions to the message object based on what was passed into the page buttons."""
        for button in GENERIC_BUTTONS:
            await self.output.add_reaction(button)

    async def _handle_transition(self):
        """Dictionary mapping of reactions to methods to be called when handling user input on a button."""
        transition_map = {GENERIC_BUTTONS[0]: self._previous, GENERIC_BUTTONS[1]: self.cancel, GENERIC_BUTTONS[2]: self._next}
        await transition_map[self.input]()
