# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2020 Rob Wagner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple

from discord import Embed, Message
from discord.abc import GuildChannel
from discord.colour import Colour
from discord.ext.commands import Context

from dpymenus.exceptions import NoFinalPageError, NotEnoughPagesError
from dpymenus.page import Page


class Menu:
    """Represents a menu.

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
        data: A dictionary containing dynamic state data you wish to pass around the menu.
    """

    # Generic values used for matching against user input.
    generic_confirm = ('y', 'yes', 'ok', 'k', 'kk', 'ready', 'rdy', 'r', 'confirm', 'okay')
    generic_deny = ('n', 'no', 'deny', 'negative', 'back', 'return')
    generic_quit = ('e', 'exit', 'q', 'quit', 'stop', 'x', 'cancel', 'c')

    def __init__(self, ctx: Context, pages: List[Page], capture_fields: Dict[str, Any] = None):
        self.ctx = ctx
        self.pages = pages
        self.page: int = 0
        self.delay: float = 0.250
        self.active: bool = True
        self.input: Optional[Message] = None
        self.output: Optional[Message] = None
        self.data = capture_fields if capture_fields else {}

        self._validate_pages()

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, capture_fields={({k: v for k, v in self.data.items()})}, delay={self.delay}, active={self.active} page={self.page}>'

    async def run(self) -> None:
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        self.output = await self.ctx.send(embed=self.pages[self.page].embed)

        while self.active:
            self.input = await self._get_input()
            await self._cleanup_input()

            if await self._is_cancelled():
                return

            await self.pages[self.page].func(self)

    async def next(self, name: str = None, quiet: bool = False) -> None:
        """Sets a specific Page object to go to and calls the ``menu.send_message`` to display the embed.

        :param name: A specific Page object name. If this is not set, the next Page in the list will be called.
        :param quiet: Whether to send the message after setting the Page or not. Defaults to False.
        """

        if name is None:
            self.page += 1

            if self.pages[self.page].func is None:
                await self.close()

        else:
            for i, page in enumerate(self.pages):
                if name == page.name:
                    self.page = self.pages.index(page)
                    break

        if not quiet:
            await self.send_message(self.pages[self.page].embed)

    async def close(self) -> None:
        """Closes the active Menu instance."""
        self.active = False

    async def send_message(self, embed: Embed) -> Message:
        """Edits a message if the channel is in a Guild, otherwise sends it to the current channel."""
        if isinstance(self.ctx.channel, GuildChannel):
            return await self.output.edit(embed=embed)
        return await self.ctx.send(embed=embed)

    @classmethod
    def override_generic_values(cls, value_type: str, replacement: Tuple[str]):
        """Allows generic input matching values built into the Menu class to be overridden.

        :param value_type: Either 'confirm', 'deny', or 'quit'.
        :param replacement: A tuple containing strings of values that act as your generic input matches.
        """
        setattr(cls, f'generic_{value_type}', replacement)

    def _validate_pages(self) -> None:
        if len(self.pages) <= 1:
            raise NotEnoughPagesError('The pages list must have more than one page.')

        if self.pages[-1].func is not None:
            raise NoFinalPageError('The pages list is missing a final page. Define a Page with `None` as the func parameter.')

    async def _get_input(self) -> Message:
        """Collects user input and places it into the input attribute."""

        try:
            message = await self.ctx.bot.wait_for('message', timeout=3600, check=lambda m: m.author == self.ctx.author)

        except asyncio.TimeoutError:
            await self._timeout()

        else:
            return message

    async def _is_cancelled(self) -> bool:
        """Checks input for a cancellation string. If there is a match, it calls menu._cancelled and then returns True."""

        if self.input.content in self.generic_quit:
            await self._cancelled()
            return True
        return False

    async def _cancelled(self) -> None:
        """Sends a cancelled message."""

        embed = Embed(title=self.pages[self.page].embed.title, description='Menu selection cancelled -- no progress was saved.', color=Colour.red())
        await self.send_message(embed)

    async def _timeout(self) -> None:
        """Sends a timeout message."""

        embed = Embed(title=self.pages[self.page].embed.title, description='You timed out at menu selection -- no progress was saved.', color=Colour.red())
        await self.send_message(embed)

    async def _cleanup_input(self) -> None:
        """Deletes a Discord client user message."""
        if isinstance(self.ctx.channel, GuildChannel):
            await self.input.delete(delay=self.delay)
