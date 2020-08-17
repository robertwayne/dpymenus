import asyncio
from typing import List, Optional, Union

from discord import Embed, Message, Reaction, TextChannel, User
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus.constants import QUIT
from dpymenus.exceptions import PagesError
from dpymenus.page import Page

sessions = list()


class BaseMenu:
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
    ctx: Context
    destination: Union[Context, User, TextChannel]
    timeout: int
    pages: List[Page]
    page: Optional[Page]
    active: bool
    input: Optional[Message, Reaction]
    output: Optional[Message]

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.destination = ctx
        self.timeout = 300
        self.pages = []
        self.page = None
        self.active = True
        self.input = None
        self.output = None

    def __repr__(self):
        return f'BaseMenu(pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, ' \
               f'active={self.active} page={self.page})'

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        pass

    async def next(self):
        """Sets a specific :class:`~dpymenus.Page` to go to and calls the :func:`~send_message()` method to display the embed."""
        # we add 2 because the index is 0-based and we are checking if the next page exists
        if self.page.index + 2 > len(self.pages):
            return

        self.page = await self.get_next_page()

        await self._post_next()

    async def previous(self):
        """Helper method for quickly accessing the previous page."""
        if self.page.index - 1 < 0:
            return

        self.page = await self.get_previous_page()

        await self.send_message(self.page.embed)

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

    async def add_pages(self, pages: List[Page]):
        """Adds a list of pages to a menu, setting their index based on the position in the list.."""
        for i, page in enumerate(pages):
            page.index = i
            self.pages.append(page)

        self.page = self.pages[0]

    async def send_message(self, embed: Embed) -> Message:
        """
        Edits a message if the channel is in a Guild, otherwise sends it to the current channel.

        :param embed: A Discord :py:class:`~discord.Embed` object.
        """
        if isinstance(self.output.channel, GuildChannel):
            return await self.output.edit(embed=embed)

        self.output = await self.destination.send(embed=embed)
        return self.output

    async def cancel(self):
        """Sends a cancellation message."""
        embed = Embed(title='Cancelled', description='Menu selection cancelled.')

        # we check if the page has a callback
        if self.page.on_cancel:
            return await self.page.on_cancel()

        # we check if there's an on_cancel attr defined and if it has a value
        # if so, we override the base embed with the attr value
        if hasattr(self, 'on_cancel') and self.on_cancel:
            embed = self.on_cancel

        # we check if the menu is a PaginatedMenu and perform edits instead of sends
        if self.__class__.__name__ == 'PaginatedMenu':
            await self.output.edit(embed=embed)

        else:
            await self.send_message(embed)

        await self.close_session()
        self.active = False

    async def get_next_page(self) -> Page:
        """Utility method that returns the next page based on the current pages index."""
        return self.pages[self.page.index + 1]

    async def get_previous_page(self) -> Page:
        """Utility method that returns the previous page based on the current pages index."""
        return self.pages[self.page.index - 1]

    async def close_session(self):
        """Remove the user from the active users list."""
        sessions.remove((self.ctx.author.id, self.ctx.channel.id))

    def set_timeout(self, timeout: int):
        self.timeout = timeout

    def set_destination(self, dest: Union[User, TextChannel]):
        self.destination = dest

    # Internal Methods
    async def _post_next(self):
        """Sends a message after the `next` method is called. Closes the session if there is no callback on the next page."""
        if self.page.on_next is None:
            await self.close_session()
            self.active = False

        await self.send_message(self.page.embed)

    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if isinstance(self.output.channel, GuildChannel):
            await self.input.delete()

    async def _timeout(self):
        """Sends a timeout message."""
        embed = Embed(title='Timed Out', description='You timed out at menu selection.')

        # we check if the page has a callback
        if self.page.on_timeout:
            return await self.page.on_timeout()

        # we check if there's an on_timeout attr defined and if it has a value
        # if so, we override the base embed with the attr value
        if hasattr(self, 'on_timeout') and self.on_timeout:
            embed = self.on_timeout

        # we check if the menu is a PaginatedMenu and perform edits instead of sends
        if self.__class__.__name__ == 'PaginatedMenu':
            await self.output.edit(embed=embed)

        else:
            await self.send_message(embed)

        await self.close_session()
        self.active = False

    async def _is_cancelled(self) -> bool:
        """Checks input for a cancellation string. If there is a match, it calls the ``menu.cancel()`` method and returns True."""
        if self.input.content in QUIT:
            await self.cancel()
            return True
        return False

    async def _get_input(self) -> Message:
        """Collects user input and places it into the input attribute."""
        try:
            message = await self.ctx.bot.wait_for('message', timeout=self.timeout, check=self._check_message)

        except asyncio.TimeoutError:
            if self.page.on_timeout:
                await self.page.on_timeout()

            else:
                await self._timeout()

        else:
            return message

    def _check_message(self, m: Message) -> bool:
        """Returns true if the author is the person who responded and the channel is the same."""
        return m.author == self.ctx.author and self.output.channel == m.channel

    async def _validate_pages(self):
        """Checks that the Menu contains at least one Page."""
        if len(self.pages) <= 1:
            raise PagesError(f'There must be more than one page in a menu. Expected at least 2, found {len(self.pages)}.')

    async def _start_session(self) -> bool:
        if (self.ctx.author.id, self.ctx.channel.id) in sessions:
            return False

        sessions.append((self.ctx.author.id, self.ctx.channel.id))
        return True
