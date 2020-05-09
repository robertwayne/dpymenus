import asyncio
from typing import Callable, List, Optional, Tuple, Union

from discord import Embed, Emoji, Message, PartialEmoji
from discord.abc import GuildChannel
from discord.colour import Colour
from discord.ext.commands import Context

from dpymenus.exceptions import PagesError
from dpymenus.page import Page


class BaseMenu:
    """Represents the base menu from which TextMenu, ButtonMenu, and Poll inherit from.

    A Menu is a composable, dynamically generated object that contains state information for a user-interactable menu.
    It contains Page objects which represent new Menu states that call methods for validation and handling.

    Attributes:
        ctx: A reference to the command Context.
        timeout: How long (in seconds) to wait before timing out.
        pages: A list containing references to Page objects.
        page_index: Index value of the current page.
        page: Current Page object.
        delay: A float representing the delay between deleting message objects.
        active: Whether or not the menu is active or not.
        input: A reference to the captured user input message object.
        output: A reference to the menus output message.
        data: A dictionary containing dynamic state information.
    """

    # Generic values used for matching against user input.
    generic_confirm = ('y', 'yes', 'ok', 'k', 'kk', 'ready', 'rdy', 'r', 'confirm', 'okay')
    generic_deny = ('n', 'no', 'deny', 'negative', 'back', 'return')
    generic_quit = ('e', 'exit', 'q', 'quit', 'stop', 'x', 'cancel', 'c')

    def __init__(self, ctx: Context, timeout: int = 300):
        self.ctx = ctx
        self.timeout = timeout
        self.pages: List[Page] = []
        self.page_index: int = 0
        self.page: Optional[Page] = None
        self.delay: float = 0.250
        self.active: bool = True
        self.input: Optional[Message] = None
        self.output: Optional[Message] = None
        self.data = None

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, ' \
               f'active={self.active} page={self.page_index}>'

    async def open(self):
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        pass

    async def next(self, name: str = None):
        """Sets a specific Page object to go to and calls the ``menu.send_message()`` method to display the embed.

        :param str name: A specific Page object name. If this is not set, the next Page in the list will be called.
        """
        if name is None:
            self.page_index += 1
            self.page = self.pages[self.page_index]

        else:
            for page in self.pages:
                if page.on_next.__name__ == name:
                    self.page_index = self.pages.index(page)
                    self.page = self.pages[self.page_index]
                    break

        #  if the next page has no on_next callback, we end the menu loop
        if self.page.on_next is None:
            self.active = False

        await self.send_message(self.page)

    async def add_page(self, on_next: Optional[Callable] = None, buttons: Optional[List[Union[str, Emoji, PartialEmoji]]] = None, **kwargs) -> Page:
        """Adds a new page object to the Menu.

        :param Optional[Callable] on_next: A reference to a function that is called when ``menu.next()`` is called.
        :param List buttons: A list of reactions that will be displayed on the Page.
        :param kwargs: Discord Embed keywords for defining your Page display.
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
        """Edits a message if the channel is in a Guild, otherwise sends it to the current channel.

        :param :py:class:`Embed` embed: A Discord :py:class:`Embed` object.
        """
        if isinstance(self.ctx.channel, GuildChannel):
            return await self.output.edit(embed=embed)
        return await self.ctx.send(embed=embed)

    async def cancel(self):
        """Sends a cancelled message."""
        if self.page.on_cancel:
            return await self.page.on_cancel()

        embed = Embed(title=self.page.title, description='Menu selection cancelled -- no progress was saved.', color=Colour.red())
        await self.send_message(embed)
        self.active = False

    # Internal Methods
    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if isinstance(self.ctx.channel, GuildChannel):
            await self.input.delete(delay=self.delay)

    async def _timeout(self):
        """Sends a timeout message."""
        self.active = False

        if self.page.on_timeout:
            return await self.page.on_timeout()

        embed = Embed(title=self.page.title, description='You timed out at menu selection -- no progress was saved.', color=Colour.red())
        await self.send_message(embed)

    async def _is_cancelled(self) -> bool:
        """Checks input for a cancellation string. If there is a match, it calls the ``menu.cancel()`` method and returns True."""
        if self.input.content in self.generic_quit:
            await self.cancel()
            return True
        return False

    async def _get_input(self) -> Message:
        """Collects user input and places it into the input attribute."""
        try:
            message = await self.ctx.bot.wait_for('message', timeout=self.timeout, check=lambda m: m.author == self.ctx.author)

        except asyncio.TimeoutError:
            if self.page.on_timeout:
                await self.page.on_timeout()

            else:
                await self._timeout()

        else:
            return message

    async def _validate_pages(self):
        """Checks that the Menu contains at least one Page."""
        if len(self.pages) <= 1:
            raise PagesError(f'There must be more than one page in a menu. Expected at least 2, found {len(self.pages)}.')

    # Class Methods
    @classmethod
    def override_generic_values(cls, value_type: str, replacement: Tuple[str]):
        """Allows generic input matching values built into the Menu class to be overridden.

        :param str value_type: Either 'confirm', 'deny', or 'quit'.
        :param Tiple[str] replacement: A tuple containing strings of values that act as your generic input matches.
        """
        setattr(cls, f'generic_{value_type}', replacement)
