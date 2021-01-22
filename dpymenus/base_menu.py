import abc
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

from discord import Embed, Message, Reaction, TextChannel, User
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus.exceptions import PagesError, SessionError
from dpymenus.page import Page

PageType = TypeVar('PageType', Embed, Page, Dict)

sessions: Dict[Tuple[int, int], Any]
sessions = dict()

logger = logging.getLogger('dpymenus')
logger.addHandler(logging.NullHandler())


class BaseMenu(abc.ABC):
    """Represents the base menu from which TextMenu, ButtonMenu, and Poll inherit from.

    Attributes
        :ctx: A reference to the command Context.
        :pages: A list containing references to Page objects.
        :page: Current Page object.
        :active: Whether or not the menu is active or not.
        :input: A reference to the captured user input message object.
        :output: A reference to the menus output message.
        :history: An ordered history of pages visited by the user.
    """

    def __init__(self, ctx: Context):
        self.ctx: Context = ctx
        self.pages: List[Page] = []
        self.page: Optional[Page] = None
        self.active: bool = True
        self.input: Optional[Union[Message, Reaction]] = None
        self.output: Optional[Message] = None
        self.history: List[int] = []

    @abc.abstractmethod
    async def open(self):
        """The entry point to a new Menu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        pass

    @property
    def timeout(self) -> int:
        return getattr(self, '_timeout', 300)

    def set_timeout(self, timeout: int) -> 'BaseMenu':
        """Sets the timeout duration (in seconds) for the menu. Returns itself for fluent-style chaining."""
        self._timeout = timeout

        return self

    @property
    def destination(self) -> Union[Context, User, TextChannel]:
        return getattr(self, '_destination', self.ctx)

    def set_destination(self, dest: Union[User, TextChannel]) -> 'BaseMenu':
        """Sets the message destination for the menu. Returns itself for fluent-style chaining."""
        self._destination = dest

        return self

    @property
    def command_message(self) -> bool:
        return getattr(self, '_command_message', False)

    def show_command_message(self) -> 'BaseMenu':
        """Persists user command invocation messages in the chat instead of deleting them after execution."""
        self._command_message = True

        return self

    @property
    def persist(self) -> bool:
        return getattr(self, '_persist', False)

    def persist_on_close(self) -> 'BaseMenu':
        """Prevents message cleanup from running when a menu closes."""
        self._persist = True

        return self

    async def close(self):
        """Helper method to close the menu out properly. Used to manually call a cancel event."""
        await self._execute_cancel()

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

        await self._post_next()

    async def to_first(self):
        """Helper method to jump to the first page."""
        self.page = self.pages[0]

        await self._post_next()

    async def to_last(self):
        """Helper method to jump to the last page."""
        self.page = self.pages[-1:][0]

        await self._post_next()

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
                if p.on_next_event.__name__ == page:
                    self.page = p
                    break

        await self._post_next()

    def last_visited_page(self) -> int:
        """Returns the last visited pages index."""
        return self.history[-2] if len(self.history) > 1 else 0

    def add_pages(self, pages: List[PageType]) -> 'BaseMenu':
        """Adds a list of pages to a menu, setting their index based on the position in the list."""
        self._validate_pages(pages)

        for i, page in enumerate(pages):
            if type(page) == Embed:
                page = Page.from_dict(page.to_dict())

            page.index = i
            self.pages.append(page)

        self.page = self.pages[0]

        return self

    async def send_message(self, page: PageType) -> Message:
        """
        Edits a message if the channel is in a Guild, otherwise sends it to the current channel.

        :param page: A Discord :py:class:`~discord.Embed` or :class:`~dpymenus.Page` object.
        """
        safe_embed = page.as_safe_embed() if type(page) == Page else page

        if isinstance(self.output.channel, GuildChannel):
            return await self.output.edit(embed=safe_embed)

        else:
            await self.output.delete()

        self.output = await self.destination.send(embed=safe_embed)
        return self.output

    @staticmethod
    async def flush():
        """Helper method that will clear the user sessions list. Only call this if you know what you are doing."""
        sessions.clear()

    # Internal Methods
    async def _open(self):
        if not self.pages:
            return

        self._start_session()

        self.output = await self.destination.send(embed=self.page.as_safe_embed())
        self.input = self.ctx.message
        self.history.append(self.page.index)

        await self._cleanup_input()

    async def _post_next(self):
        """Sends a message after the `next` method is called. Closes the session if there is no callback on the next page."""
        if self.__class__.__name__ != 'PaginatedMenu':
            if self.page.on_next_event is None:
                await self.close_session()
                self.active = False

        self.history.append(self.page.index)
        await self.send_message(self.page)

    async def _execute_cancel(self):
        """Sends a cancellation message if set and closes the menu."""
        # we check if the page has a callback
        if self.page.on_cancel_event:
            return await self.page.on_cancel_event()

        cancel_page = getattr(self, 'cancel_page', None)

        if cancel_page:
            await self.output.edit(embed=cancel_page)

        else:
            await self._cleanup_output()

        await self.close_session()

    async def close_session(self):
        """Remove the user from the active users list."""
        del sessions[(self.ctx.author.id, self.ctx.channel.id)]
        self.active = False

    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if not self.command_message:
            if isinstance(self.input.channel, GuildChannel):
                await self.input.delete()

    async def _cleanup_output(self):
        """Deletes the Discord client bot message."""
        self.output: Message

        await self.output.clear_reactions()

        if not self.persist:
            await self.output.delete()
            self.output = None

    async def _execute_timeout(self):
        """Sends a timeout message if set and closes the menu."""
        if self.page.on_timeout_event:
            return await self.page.on_timeout_event()

        try:
            await self.close_session()

        except KeyError:
            return

        timeout_page = getattr(self, 'timeout_page', None)

        if timeout_page:
            await self.output.edit(embed=timeout_page)

        else:
            await self._cleanup_output()

        self.active = False

    async def _get_input(self) -> Message:
        """Collects user input and places it into the input attribute."""
        try:
            message = await self.ctx.bot.wait_for('message', timeout=self.timeout, check=self._check_message)

        except asyncio.TimeoutError:
            if self.page.on_timeout_event:
                await self.page.on_timeout_event()

            else:
                await self._execute_timeout()

        else:
            return message

    def _check_message(self, m: Message) -> bool:
        """Returns true if the author is the person who responded and the channel is the same."""
        return (m.author == self.ctx.author
                and self.output.channel == m.channel)

    @staticmethod
    def _validate_pages(pages: List[Any]):
        """Checks that the Menu contains at least one pages."""
        if len(pages) == 0:
            raise PagesError(f'There must be at least one page in a menu. Expected at least 1, found {len(pages)}.')

    def _start_session(self):
        """Starts a new user session in the sessions storage. Raises a SessionError if the key already exists."""
        if (self.ctx.author.id, self.ctx.channel.id) in sessions.keys():
            raise SessionError(f'Duplicate session in channel [{self.ctx.channel.id}] for user [{self.ctx.author.id}].')
        else:
            sessions.update({(self.ctx.author.id, self.ctx.channel.id): self})
            return True
