import asyncio
from typing import List, Union

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
        self.page_numbers: bool = False
        self.skip_buttons: bool = False
        self.buttons: List = []

    def __repr__(self):
        return f'PaginatedMenu(pages={[p.__str__() for p in self.pages]}, page={self.page}, timeout={self.timeout}, ' \
               f'skip_buttons={self.skip_buttons} page_numbers={self.page_numbers}, cancel_page={self.cancel_page}, ' \
               f'timeout_page={self.timeout_page})'

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super()._open()
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

    def add_pages(self, embeds: List[Embed]) -> 'PaginatedMenu':
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

        return self

    @property
    def cancel_page(self):
        return getattr(self, '_cancel_page', None)

    def set_cancel_page(self, func: Embed) -> 'PaginatedMenu':
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style chaining."""
        self._cancel_page = func

        return self

    @property
    def timeout_page(self):
        return getattr(self, '_timeout_page', None)

    def set_timeout_page(self, func: Embed) -> 'PaginatedMenu':
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style chaining."""
        self._timeout_page = func

        return self

    def show_page_numbers(self) -> 'PaginatedMenu':
        """Adds page numbers to each embeds by overwriting the footer. Returns itself for fluent-style chaining."""
        self.page_numbers = True

        return self

    def enable_skip_buttons(self) -> 'PaginatedMenu':
        """Adds two extra buttons for jumping to the first and last page. Returns itself for fluent-style chaining."""
        self.skip_buttons = True

        return self

    def set_buttons(self, buttons: List) -> 'PaginatedMenu':
        """Replaces the default butttons. You must include 3 or 5 emoji/strings in the order they would be displayed.
        0 and 5 are only shown if `enable_skip_buttons` is set, otherwisee 2, 3, and 4 will be shown. You can pass in
        `None` or an empty string for 0 and 5 if you do not intend on using them. If you only pass in 3 values, they
         will be filled in as the defaults for you. If you enable the skip buttons without having values set, it will
         use those defaults."""
        self.buttons = []

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
        if self.skip_buttons:
            for button in GENERIC_BUTTONS:
                await self.output.add_reaction(button)

        else:
            for button in GENERIC_BUTTONS[1:4]:
                await self.output.add_reaction(button)

    async def _handle_transition(self):
        """Dictionary mapping of reactions to methods to be called when handling user input on a button."""
        transitions = [self.to_first, self.previous, self.cancel, self.next, self.to_last]

        if self.buttons:
            if len(self.buttons) == 3:
                self.buttons.insert(0, GENERIC_BUTTONS[0])
                self.buttons.insert(5, GENERIC_BUTTONS[4])

            transition_map = {button: transition for button, transition in zip(self.buttons, transitions)}

        else:
            transition_map = {GENERIC_BUTTONS[0]: self.to_first, GENERIC_BUTTONS[1]: self.previous, GENERIC_BUTTONS[2]: self.cancel,
                              GENERIC_BUTTONS[3]: self.next, GENERIC_BUTTONS[4]: self.to_last}

        await transition_map[self.input]()
