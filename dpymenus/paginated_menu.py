import asyncio
from typing import Callable, List, Union

from discord import Embed, Emoji, Message, PartialEmoji, Reaction
from discord.abc import GuildChannel, User
from discord.ext.commands import Context

from dpymenus import ButtonMenu, Page
from dpymenus.constants import GENERIC_BUTTONS


class PaginatedMenu(ButtonMenu):
    """
    Represents an paginated, button-based response menu.

    :param ctx: A reference to the command context.
    """

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.page_numbers = False
        self.on_cancel = None
        self.on_timeout = None

    def __repr__(self):
        return f'PaginatedMenu(pages={[p.__str__() for p in self.pages]}, page={self.page}, timeout={self.timeout}, ' \
               f'page_numbers={self.page_numbers}, timeout={self.timeout}, on_timeout={self.on_timeout}, on_cancel={self.on_cancel})'

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super()._validate_pages()

        if await self._start_session() is False:
            return

        self.output = await self.destination.send(embed=self.page.embed)

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
        """Helper method to convert embeds into Pagees and add them to a menu.

        :param embeds: A list of Discord :py:class:`~discord.Embed` objects.
        """
        for i, embed in enumerate(embeds):
            if self.page_numbers:
                embed.set_footer(text=f'{i + 1}/{len(embeds)}')

            p = Page(embed)
            p.index = i
            self.pages.append(p)

        self.page = self.pages[0]

    def set_event_cancel(self, func: Callable):
        self.on_cancel = func

        return self

    def set_event_timeout(self, func: Callable):
        self.on_timeout = func

        return self

    def show_page_numbers(self):
        self.page_numbers = True

        return self

    def hide_page_numbers(self):
        self.page_numbers = False

        return self

    # Internal Methods
    async def _get_reaction(self) -> Union[Emoji, str]:
        """Collects a user reaction and places it into the input attribute. Returns a :py:class:`discord.Emoji` or string."""
        reaction, user = await self.ctx.bot.wait_for('reaction_add',
                                                     check=self._check_reaction)

        if isinstance(reaction.emoji, (Emoji, PartialEmoji)):
            return reaction.emoji.name
        return reaction.emoji

    async def _get_reaction_remove(self) -> Union[Emoji, str]:
        """Collects a user reaction and places it into the input attribute. Returns a :py:class:`discord.Emoji` or string."""
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
        transition_map = {GENERIC_BUTTONS[0]: self.previous, GENERIC_BUTTONS[1]: self.cancel, GENERIC_BUTTONS[2]: self.next}
        await transition_map[self.input]()
