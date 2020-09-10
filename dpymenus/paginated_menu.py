import asyncio
from typing import List, Optional, Union

from discord import Embed, Emoji, Message, RawReactionActionEvent
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import ButtonMenu, Page
from dpymenus.base_menu import EmbedPage
from dpymenus.constants import GENERIC_BUTTONS


class PaginatedMenu(ButtonMenu):
    """
    Represents an paginated, button-based response menu.

    :param ctx: A reference to the command context.
    """

    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def __repr__(self):
        return f'PaginatedMenu(pages={[p.__str__() for p in self.pages]}, page={self.page}, timeout={self.timeout}, ' \
               f'skip_buttons={self.skip_buttons} page_numbers={self.page_numbers}, cancel_page={self.cancel_page}, ' \
               f'timeout_page={self.timeout_page})'

    @property
    def cancel_page(self) -> Optional[Embed]:
        return getattr(self, '_cancel_page', None)

    def set_cancel_page(self, embed: Embed) -> 'PaginatedMenu':
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style chaining."""
        self._cancel_page = embed

        return self

    @property
    def timeout_page(self) -> Optional[Embed]:
        return getattr(self, '_timeout_page', None)

    def set_timeout_page(self, embed: Embed) -> 'PaginatedMenu':
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style chaining."""
        self._timeout_page = embed

        return self

    @property
    def page_numbers(self) -> bool:
        return getattr(self, '_page_numbers', False)

    def show_page_numbers(self) -> 'PaginatedMenu':
        """Adds page numbers to each embeds by overwriting the footer. Returns itself for fluent-style chaining."""
        self._page_numbers = True

        return self

    @property
    def skip_buttons(self) -> bool:
        return getattr(self, '_skip_buttons', False)

    def show_skip_buttons(self) -> 'PaginatedMenu':
        """Adds two extra buttons for jumping to the first and last page. Returns itself for fluent-style chaining."""
        self._skip_buttons = True

        return self

    @property
    def cancel_button(self) -> bool:
        return getattr(self, '_cancel_button', True)

    def hide_cancel_button(self) -> 'PaginatedMenu':
        """Sets whether to show the cancel button or not. Returns itself for fluent-style chaining."""
        self._cancel_button = False

        return self

    @property
    def buttons_list(self) -> List:
        return getattr(self, '_buttons_list', [])

    def buttons(self, buttons: List) -> 'PaginatedMenu':
        """Replaces the default butttons. You must include 3 or 5 emoji/strings in the order they would be displayed.
        0 and 5 are only shown if `enable_skip_buttons` is set, otherwisee 2, 3, and 4 will be shown. You can pass in
        `None` or an empty string for 0 and 5 if you do not intend on using them. If you only pass in 3 values, they
         will be filled in as the defaults for you. If you enable the skip buttons without having values set, it will
         use those defaults."""
        self._buttons_list = buttons

        if len(buttons) == 3:
            self.buttons_list.insert(0, GENERIC_BUTTONS[0])
            self.buttons_list.insert(4, GENERIC_BUTTONS[4])

        return self

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await super()._open()
        await self._add_buttons()

        while self.active:
            done, pending = await asyncio.wait([asyncio.create_task(self._get_reaction_add()),
                                                asyncio.create_task(self._get_reaction_remove())],
                                               return_when=asyncio.FIRST_COMPLETED,
                                               timeout=self.timeout)

            # if we both tasks are still pending, we force a timeout by manually calling cleanup methods
            if len(pending) == 2:
                await self._execute_timeout()

            else:
                for future in done:
                    self.input = future.result()

                if isinstance(self.output.channel, GuildChannel):
                    await self.output.remove_reaction(self.input, self.ctx.author)

                await self._handle_transition()

            for task in pending:
                task.cancel()

        if self.output:
            await self._cleanup_reactions()

    async def send_message(self, embed: Embed) -> Message:
        """
        Edits the menu output message. We override the :class:`~dpymenus.BaseMenu` implementation because
        we always want to edit, even in a DM channel type.

        :param embed: A Discord :py:class:`~discord.Embed` object.
        """
        return await self.output.edit(embed=embed)

    def add_pages(self, pages: List[EmbedPage]) -> 'PaginatedMenu':
        """Helper method to convert embeds into Pagees and add them to a menu."""
        for i, page in enumerate(pages):
            if type(page) == Embed:
                page = Page.from_dict(page.to_dict())

            if self.page_numbers:
                page.set_footer(text=f'{i + 1}/{len(pages)}')

            page.index = i
            self.pages.append(page)

        self.page = self.pages[0]

        return self

    async def _execute_cancel(self):
        """Sends a cancellation message. Deletes the menu message if no page was set."""
        cancel_page = getattr(self, 'cancel_page', None)

        if cancel_page:
            await self.output.edit(embed=cancel_page)

        else:
            await self._cleanup_output()

        await self.close_session()
        self.active = False

    # Internal Methods
    async def _execute_timeout(self):
        """Sends a timeout message. Deletes the menu message if no page was set."""
        timeout_page = getattr(self, 'timeout_page')

        if timeout_page:
            await self.output.edit(embed=timeout_page)

        else:
            await self._cleanup_output()

        await self.close_session()
        self.active = False

    async def _get_reaction_add(self) -> Union[Emoji, str]:
        """Collects a user reaction and places it into the input attribute. Returns a :py:class:`discord.Emoji` or string."""
        reaction_event = await self.ctx.bot.wait_for('raw_reaction_add', check=self._check_reaction)

        return reaction_event.emoji.name

    async def _get_reaction_remove(self) -> Union[Emoji, str]:
        """Collects a user reaction and places it into the input attribute. Returns a :py:class:`discord.Emoji` or string."""
        reaction_event = await self.ctx.bot.wait_for('raw_reaction_remove', check=self._check_reaction)

        return reaction_event.emoji.name

    def _check_reaction(self, event: RawReactionActionEvent) -> bool:
        """Returns true if the author is the person who reacted and the message ID's match. Checks the generic buttons."""

        if event.emoji.name in self.buttons_list:
            return event.user_id == self.ctx.author.id and event.message_id == self.output.id
        return False

    async def _add_buttons(self):
        """Adds reactions to the message object based on what was passed into the page buttons."""
        # sets generic buttons to the instance if nothing has been set
        if not self.buttons_list:
            self.buttons(GENERIC_BUTTONS)

        # remove the cancel button if hide_cancel_button is true
        if not self.cancel_button:
            self.buttons_list[2] = None

        if self.skip_buttons:
            for button in self.buttons_list:
                if button is None:
                    continue

                await self.output.add_reaction(button)

        else:
            for button in self.buttons_list[1:4]:
                if button is None:
                    continue

                await self.output.add_reaction(button)

    async def _handle_transition(self):
        """Dictionary mapping of reactions to methods to be called when handling user input on a button."""
        transitions = [self.to_first, self.previous, self.close, self.next, self.to_last]
        transition_map = {button: transition for button, transition in zip(self.buttons_list, transitions)}

        await transition_map[self.input]()
