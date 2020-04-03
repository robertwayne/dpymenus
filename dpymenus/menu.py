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
from typing import Dict, List, Optional

from discord import Embed, Message
from discord.abc import GuildChannel
from discord.colour import Colour
from discord.ext.commands import Bot, Context

from dpymenus.exceptions import NoFinalPageError, NotEnoughPagesError
from dpymenus.page import Page


class Menu:
    """Represents a menu.

    A Menu is a composable, dynamically generated object that contains state information for a user-interactable menu.
    It contains Page objects which represent new Menu states that call methods for validation and handling.

    Attributes:
        client: A reference to the bot client.
        ctx: A reference to the command Context.
        active: Whether or not the menu is active or not.
        message: Reference to the Discord Message object that contains the Page embed.
        input_message: Reference to the Discord Message object that contains player input.
        page: Reference to the current Page object.
        pages: A list containing references to Page objects.
        delay: A float representing the delay between deleting message objects.
    """

    def __init__(self, client: Bot, ctx: Context, pages: List[Page], capture_fields: Dict[str, Optional[str]] = None):
        self.client = client
        self.ctx = ctx
        self.pages = pages
        self.page = pages[0]
        self.delay = 0.250
        self.active = True
        self.message = None
        self.input_message = None

        if capture_fields:
            self._capture(capture_fields)

    def __str__(self):
        return f'Pages: {self.pages}\nCurrent Page: {self.page}\n{self.input_message}\n{self.message}'

    def __repr__(self):
        return f'Menu({self.client}, {self.ctx}, {self.message}, {self.input_message}, {self.input_message}, {self.page}, {self.pages})'

    async def run(self) -> None:
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        self.message = await self.ctx.send(embed=self.page.embed)

        while self.active:
            self.input_message = await self._get_input()
            await self._cleanup_input()

            if await self._is_cancelled():
                return

            await self.page.func(self)

    async def next_page(self, specific_page: str = None, quiet_output: bool = False) -> None:
        """Sets a specific Page object to go to and calls the ``menu.send_message`` to display the embed.

        :param specific_page: A specific Page object name. If this is not set, the next Page in the list will be called.
        :param quiet_output: Whether to send the message after setting the Page or not. Defaults to False.
        """

        for i, page in enumerate(self.pages):
            if specific_page and page.name == specific_page:
                self.page = page
            else:
                if len(self.pages) - 1 >= self.pages[::-1].index(self.pages[-1]) - 1:
                    self.page = self.pages[-1]
                    await self.close()
                else:
                    self.page = self.pages[i]

        if not quiet_output:
            await self._send_message(self.page.embed)

    async def close(self) -> None:
        """Closes the active Menu instance."""
        self.active = False

    def _capture(self, captures: Dict[str, Optional[str]]) -> None:
        """Accepts a dictionary of strings that you wish to store data They can take a default
        value (to pass data among local methods), or None to imply collection needed via a get_input method.

        Applies these attributes and values dynamically on the Menu instance.

        :param captures: A dictionary containing fields that should be dynamically set on the menu instance. Can contain default values or None.
        """

        for attr, value in captures.items():
            self.__setattr__(attr, value)

    async def _validate_pages(self) -> None:
        if len(self.pages) <= 1:
            raise NotEnoughPagesError('The pages list must have more than one page.')

        if self.pages[-1].func is not None:
            raise NoFinalPageError('The pages list is missing a final page. Define a Page with `None` as the func parameter.')

    async def _get_input(self) -> Message:
        """Collects user input and places it into the input_message attribute."""

        try:
            message = await self.client.wait_for('message', timeout=3600, check=lambda m: m.author == self.ctx.author)

        except asyncio.TimeoutError:
            await self._timeout()

        else:
            return message

    async def _is_cancelled(self) -> bool:
        """Checks user_input for a cancellation string. If found, calls menu._cancelled and then returns True."""

        if self.input_message.content in ('e', 'exit', 'q', 'quit', 'stop', 'x', 'cancel', 'c'):
            await self._cancelled()
            return True
        return False

    async def _cancelled(self) -> None:
        """Sends a cancelled message."""

        embed = Embed(title=self.page.embed.title, description='Menu selection cancelled -- no progress was saved.', color=Colour.red())
        await self._send_message(embed)

    async def _timeout(self) -> None:
        """Sends a timeout message."""

        embed = Embed(title=self.page.embed.title, description='You timed out at menu selection -- no progress was saved.', color=Colour.red())
        await self._send_message(embed)

    async def _cleanup_input(self) -> None:
        """Deletes a Discord client user message."""
        if isinstance(self.ctx.channel, GuildChannel):
            await self.input_message.delete(delay=self.delay)

    async def _send_message(self, embed: Embed) -> Message:
        """Edits a message if the channel is in a Guild, otherwise sends it to the current channel."""
        if isinstance(self.ctx.channel, GuildChannel):
            return await self.message.edit(embed=embed)
        return await self.ctx.send(embed=embed)
