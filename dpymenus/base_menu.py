import asyncio
from typing import Callable, List, Optional, Union

from discord import Embed, Emoji, Message, PartialEmoji, TextChannel, User
from discord.abc import GuildChannel
from discord.colour import Colour
from discord.ext.commands import Context

from dpymenus.constants import QUIT
from dpymenus.exceptions import PagesError
from dpymenus.page import Page

sessions = list()


class BaseMenu:
    """Represents the base menu from which TextMenu, ButtonMenu, and Poll inherit from.

    A Menu is a composable, dynamically generated object that contains state information for a user-interactable menu.
    It contains Page objects which represent new Menu states that call methods for validation and handling.

    Attributes
        :ctx: A reference to the command Context.
        :timeout: How long (in seconds) to wait before timing out.
        :destination: Whether the menu will open in the current channel, sent to a seperate guild channel, or sent to a DM channel.
        :pages: A list containing references to Page objects.
        :page_index: Index value of the current page.
        :page: Current Page object.
        :active: Whether or not the menu is active or not.
        :input: A reference to the captured user input message object.
        :output: A reference to the menus output message.
        :data: A dictionary containing dynamic state information.
    """

    def __init__(self, ctx: Context, timeout: int = 300, destination: Optional[Union[TextChannel, User]] = None):
        self.ctx = ctx
        self.timeout = timeout
        self.destination = ctx if destination is None else destination
        self.pages: List[Page] = []
        self.page_index: int = 0
        self.page: Optional[Page] = None
        self.active: bool = True
        self.input: Optional[Message] = None
        self.output: Optional[Message] = None
        self.data = None

    def __repr__(self):
        return f'BaseMenu(pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, ' \
               f'active={self.active} page={self.page_index})'

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        pass

    async def next(self, name: Optional[Union[str, int]] = None):
        """Sets a specific :class:`~dpymenus.Page` to go to and calls the :func:`~send_message()` method to display the embed.

        :param name: A specific page object name or its index. If this is not set, the next page in the list will be called.
        """
        if name is None:
            self.page_index += 1
            self.page = self.pages[self.page_index]

        else:
            if isinstance(name, str):
                # get a page index from its on_next callback function name and assign it
                for page in self.pages:
                    if page.on_next.__name__ == name:
                        self.page_index = self.pages.index(page)
                        self.page = self.pages[self.page_index]
                        break

            elif isinstance(name, int):
                # get a page index from its index and assign it
                self.page_index = name
                self.page = self.pages[name]

        #  if the next page has no on_next callback, we end the menu loop
        if self.page.on_next is None:
            await self.close_session()
            self.active = False

        await self.send_message(self.page)

    async def previous(self):
        """Helper method for quickly accessing the previous page."""
        if self.page_index - 1 < 0:
            return

        self.page_index -= 1
        self.page = self.pages[self.page_index]

        await self.send_message(self.page)

    async def add_page(self, on_next: Optional[Callable] = None, buttons: Optional[List[Union[str, Emoji, PartialEmoji]]] = None, **kwargs) -> Page:
        """Adds a new page object to the Menu.

        :param on_next: A reference to a function that is called when :func:`~next()` is called.
        :param buttons: A list of reactions that will be displayed on the page.
        :param kwargs: :py:class:`~discord.Embed` arguments for defining your Page display.
        """
        page = Page(on_next=on_next, buttons=buttons, **kwargs)
        self.pages.append(page)

        if self.pages:
            self.page = self.pages[0]

        return page

    async def add_pages(self, pages: List[Page]):
        """Helper method to add a list of pre-instantiated pages to a menu."""
        for page in pages:
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
        embed = Embed(title='Cancelled', description='Menu selection cancelled.', color=Colour.red())

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
        return self.pages[self.page_index + 1]

    async def close_session(self):
        """Remove the user from the active users list."""
        sessions.remove((self.ctx.author.id, self.ctx.channel.id))

    # Internal Methods
    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if isinstance(self.output.channel, GuildChannel):
            await self.input.delete()

    async def _timeout(self):
        """Sends a timeout message."""
        embed = Embed(title='Timed Out', description='You timed out at menu selection.', color=Colour.red())

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
            message = await self.ctx.bot.wait_for('message', timeout=self.timeout,
                                                  check=self._check_message)

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
