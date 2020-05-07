import asyncio
from typing import List, Optional, Tuple

from discord import Embed, Message
from discord.abc import GuildChannel
from discord.colour import Colour
from discord.ext.commands import Context

from dpymenus.exceptions import NotEnoughPagesError
from dpymenus.page import Page


class BaseMenu:
    """Represents the base menu from which TextMenu, ButtonMenu, and Poll inherit from.

    A Menu is a composable, dynamically generated object that contains state information for a user-interactable menu.
    It contains Page objects which represent new Menu states that call methods for validation and handling.

    Attributes:
        ctx: A reference to the command Context.
        pages: A list containing references to Page objects.
        page: Index value of the current page.
        delay: A float representing the delay between deleting message objects.
        active: Whether or not the menu is active or not.
        input: A reference to the captured user input message object.
        output: A reference to the menus output message.
        timeout: How long (in seconds) to wait before timing out.
    """

    # Generic values used for matching against user input.
    generic_confirm = ('y', 'yes', 'ok', 'k', 'kk', 'ready', 'rdy', 'r', 'confirm', 'okay')
    generic_deny = ('n', 'no', 'deny', 'negative', 'back', 'return')
    generic_quit = ('e', 'exit', 'q', 'quit', 'stop', 'x', 'cancel', 'c')

    def __init__(self, ctx: Context, pages: List[Page], timeout: int = 300):
        self.ctx = ctx
        self.pages = pages
        self.timeout = timeout
        self.page: int = 0
        self.type: Optional[str] = None
        self.delay: float = 0.250
        self.active: bool = True
        self.input: Optional[Message] = None
        self.output: Optional[Message] = None

        self._validate_pages()

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, ' \
               f'active={self.active} page={self.page}>'

    async def run(self):
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        pass

    async def next(self, name: str = None):
        """Sets a specific Page object to go to and calls the ``menu.send_message`` to display the embed.

        :param str name: A specific Page object name. If this is not set, the next Page in the list will be called.
        """
        if name is None:
            self.page += 1

        else:
            for page in self.pages:
                if page.func.__name__ == name:
                    self.page = self.pages.index(page)
                    break

        if self.pages[self.page].func is None:
            await self.close()

        await self.send_message(self.pages[self.page])

    async def cancel(self):
        """Sends a cancelled message."""
        embed = Embed(title=self.pages[self.page].title, description='Menu selection cancelled -- no progress was saved.', color=Colour.red())
        await self.send_message(embed)
        await self.close()  # explicitly close the menu so reactive pages require less code

    async def send_message(self, embed: Embed) -> Message:
        """Edits a message if the channel is in a Guild, otherwise sends it to the current channel.

        :param :py:class:`Embed` embed: A Discord :py:class:`Embed` object.
        """
        if isinstance(self.ctx.channel, GuildChannel):
            return await self.output.edit(embed=embed)
        return await self.ctx.send(embed=embed)

    async def close(self):
        """Closes the active Menu instance."""
        self.active = False

    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if isinstance(self.ctx.channel, GuildChannel):
            await self.input.delete(delay=self.delay)

    async def _timeout(self):
        """Sends a timeout message."""
        embed = Embed(title=self.pages[self.page].title, description='You timed out at menu selection -- no progress was saved.', color=Colour.red())
        await self.send_message(embed)

    async def _is_cancelled(self) -> bool:
        """Checks input for a cancellation string. If there is a match, it calls menu.cancel() and then returns True."""
        if self.input.content in self.generic_quit:
            await self.cancel()
            return True
        return False

    async def _get_input(self) -> Message:
        """Collects user input and places it into the input attribute."""
        try:
            message = await self.ctx.bot.wait_for('message', timeout=self.timeout, check=lambda m: m.author == self.ctx.author)

        except asyncio.TimeoutError:
            await self._timeout()

        else:
            return message

    def _validate_pages(self):
        if len(self.pages) <= 1:
            raise NotEnoughPagesError('The pages list must have more than one page.')

    @classmethod
    def override_generic_values(cls, value_type: str, replacement: Tuple[str]):
        """Allows generic input matching values built into the Menu class to be overridden.

        :param str value_type: Either 'confirm', 'deny', or 'quit'.
        :param Tiple[str] replacement: A tuple containing strings of values that act as your generic input matches.
        """
        setattr(cls, f'generic_{value_type}', replacement)
