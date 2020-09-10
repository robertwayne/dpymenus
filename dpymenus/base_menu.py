import asyncio
from typing import List, Optional, Tuple, TypeVar, Union
from warnings import warn

from discord import Embed, Message, Reaction, TextChannel, User
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus.constants import QUIT
from dpymenus.exceptions import ButtonsError, EventError, PagesError, SessionError
from dpymenus.page import Page
import abc

TPages = TypeVar('TPages', Embed, Page)

sessions: List[Tuple[int, int]] = list()


class BaseMenu(abc.ABC):
    """Represents the base menu from which TextMenu, ButtonMenu, and Poll inherit from.

    Attributes
        :ctx: A reference to the command Context.
        :destination: Whether the menu will open in the current channel, sent to a seperate guild channel, or sent to a DM channel.
        :timeout: How long (in seconds) to wait before timing out.
        :pages: A list containing references to Page objects.
        :page: Current Page object.
        :active: Whether or not the menu is active or not.
        :input: A reference to the captured user input message object.
        :output: A reference to the menus output message.
    """

    def __init__(self, ctx: Context):
        self.ctx: Context = ctx
        self.destination: Union[Context, User, TextChannel] = ctx
        self.timeout: int = 300
        self.pages: List[Page] = []
        self.page: Optional[Page] = None
        self.active: bool = True
        self.input: Optional[Union[Message, Reaction]] = None
        self.output: Optional[Message] = None

    @abc.abstractmethod
    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        pass

    async def close(self):
        """Helper method to close the menu properly."""
        await self.close_session()
        self.active = False

    async def next(self):
        """Sets a specific :class:`~dpymenus.Page` to go to and calls the :func:`~send_message()` method to display the embed."""
        if self.page.index + 1 > len(self.pages) - 1:
            return

        self.page = self.pages[self.page.index + 1]

        await self._post_next()

    async def previous(self):
        """Helper method for quickly accessing the previous page."""
        if self.page.index - 1 < 0:
            return

        self.page = self.pages[self.page.index - 1]

        await self.send_message(self.page)

    async def to_first(self):
        """Helper method to jump to the first page."""
        self.page = self.pages[0]

        await self.send_message(self.page)

    async def to_last(self):
        """Helper method to jump to the last page."""
        self.page = self.pages[-1:][0]

        await self.send_message(self.page)

    async def go_to(self, page: Optional[Union[str, int]] = None):
        """Sets a specific :class:`~dpymenus.Page` to go to and calls the :func:`~send_message()` method to display the embed.

        :param page: The name of the `on_next` function for a particular page or its page number. If this is not set, the next
        page in the list will be called.
        """
        if isinstance(page, int):
            self.page = self.pages[page]

        elif isinstance(page, str):
            # get a page index from its on_next callback function name and assign it
            for p in self.pages:
                if p.on_next.__name__ == page:
                    self.page = p
                    break

        await self._post_next()

    def add_pages(self, pages: List[TPages]) -> 'BaseMenu':
        """Adds a list of pages to a menu, setting their index based on the position in the list.."""
        for i, page in enumerate(pages):
            if type(page) == Embed:
                page = Page.from_dict(page.to_dict())

            page.index = i
            self.pages.append(page)

        self.page = self.pages[0]

        return self

    async def send_message(self, embed: Union[Page, Embed]) -> Message:
        """
        Edits a message if the channel is in a Guild, otherwise sends it to the current channel.

        :param embed: A Discord :py:class:`~discord.Embed` object.
        """
        if isinstance(self.output.channel, GuildChannel):
            return await self.output.edit(embed=embed)

        self.output = await self.destination.send(embed=embed)
        return self.output

    async def _cancel(self):
        """Sends a cancellation message."""
        # we check if the page has a callback
        if self.page.on_cancel_event:
            return await self.page.on_cancel_event()

        embed = Embed(title='Cancelled', description='Menu selection cancelled.')
        await self.send_message(embed)

        await self.close_session()
        self.active = False

    async def close_session(self):
        """Remove the user from the active users list."""
        sessions.remove((self.ctx.author.id, self.ctx.channel.id))

    def set_timeout(self, timeout: int) -> 'BaseMenu':
        """Sets the timeout duration for the menu. Returns itself for fluent-style chaining."""
        self.timeout = timeout

        return self

    def set_destination(self, dest: Union[User, TextChannel]) -> 'BaseMenu':
        """Sets the message destination for the menu. Returns itself for fluent-style chaining."""
        self.destination = dest

        return self

    @staticmethod
    async def flush():
        """Helper method that will clear the user sessions list. Only call this if you know what you are doing."""
        sessions.clear()

    # Internal Methods
    async def _open(self):
        self._validate_pages()
        self._start_session()

        self.output = await self.destination.send(embed=self.page)
        self.input = self.ctx.message
        await self._cleanup_input()

    async def _post_next(self):
        """Sends a message after the `next` method is called. Closes the session if there is no callback on the next page."""
        if self.__class__.__name__ != 'PaginatedMenu':
            if self.page.on_next_event is None:
                await self.close_session()
                self.active = False

        await self.send_message(self.page)

    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if isinstance(self.input.channel, GuildChannel):
            await self.input.delete()

    async def _cleanup_output(self):
        """Deletes the Discord client bot message."""
        self.output: Message
        await self.output.delete()
        self.output = None

    async def _timeout(self):
        """Sends a timeout message."""
        # we check if the page has a callback
        if self.page.on_timeout_event:
            return await self.page.on_timeout_event()

        embed = Embed(title='Timed Out', description='You timed out at menu selection.')
        await self.send_message(embed)

        await self.close_session()
        self.active = False

    def _is_cancelled(self) -> bool:
        """Checks input for a cancellation string. If there is a match, it calls the ``menu.cancel()`` method and returns True."""
        if self.input.content in QUIT:
            return True
        return False

    async def _get_input(self) -> Message:
        """Collects user input and places it into the input attribute."""
        try:
            message = await self.ctx.bot.wait_for('message', timeout=self.timeout, check=self._check_message)

        except asyncio.TimeoutError:
            if self.page.on_timeout_event:
                await self.page.on_timeout_event()

            else:
                await self._timeout()

        else:
            return message

    def _check_message(self, m: Message) -> bool:
        """Returns true if the author is the person who responded and the channel is the same."""
        return m.author == self.ctx.author and self.output.channel == m.channel

    def _validate_pages(self):
        """Checks that the Menu contains at least one Page."""
        if len(self.pages) <= 1:
            raise PagesError(f'There must be more than one page in a menu. Expected at least 2, found {len(self.pages)}.')

    def _start_session(self) -> bool:
        if (self.ctx.author.id, self.ctx.channel.id) in sessions:
            return False

        sessions.append((self.ctx.author.id, self.ctx.channel.id))
        return True

    def _validate_buttons(self):
        """Ensures that a menu was passed the appropriate amount of buttons."""
        _cb_count = 0
        for page in self.pages:
            if not page.buttons_list:
                break

            if page.on_next_event:
                _cb_count += 1

            if len(page.buttons_list) < 1:
                raise ButtonsError('Any page with an `on_next` event capture must have at least one button.\n'
                                   f'{page} {page.title} only has {len(page.buttons_list)} buttons.')

            if len(page.buttons_list) > 5:
                warn('Adding more than 5 buttons to a page at once may result in discord.py throttling the bot client.')

        if self.page.on_fail_event:
            raise EventError('A ButtonMenu can not capture an `on_fail` event.')

        if _cb_count < len(self.pages) - 1:
            raise EventError(f'ButtonMenu missing `on_next` captures. Expected {len(self.pages) - 1}, found {_cb_count}.')
