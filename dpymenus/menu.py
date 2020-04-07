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

from discord import Embed, Emoji, Message, PartialEmoji
from discord.abc import GuildChannel
from discord.colour import Colour
from discord.ext.commands import Context

from dpymenus.exceptions import NotEnoughPagesError
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
        state_fields: A dictionary containing dynamic state state_fields you wish to pass around the menu.
    """

    # Generic values used for matching against user input.
    generic_confirm = ('y', 'yes', 'ok', 'k', 'kk', 'ready', 'rdy', 'r', 'confirm', 'okay')
    generic_deny = ('n', 'no', 'deny', 'negative', 'back', 'return')
    generic_quit = ('e', 'exit', 'q', 'quit', 'stop', 'x', 'cancel', 'c')

    def __init__(self, ctx: Context, pages: List[Page], state_fields: Dict[str, Any] = None):
        self.ctx = ctx
        self.pages = pages
        self.page: int = 0
        self.delay: float = 0.250
        self.active: bool = True
        self.input: Optional[Message] = None
        self.output: Optional[Message] = None
        self.state_fields = state_fields if state_fields else {}

        self._validate_pages()

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, capture_fields={({k: v for k, v in self.state_fields.items()})}, delay={self.delay}, active={self.active} page={self.page}>'

    async def run(self) -> None:
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        self.output = await self.ctx.send(embed=self.pages[self.page])

        while self.active:
            if self.pages[self.page].buttons:
                await self.add_buttons()

            if self.pages[self.page].buttons is None:
                self.input = await self._get_input()
                await self._cleanup_input()

                if await self._is_cancelled():
                    return

            else:
                self.input = await self._get_reaction()
                await self._cleanup_reactions()

            await self.pages[self.page].func(self)

    async def next(self, name: str = None) -> None:
        """Sets a specific Page object to go to and calls the ``menu.send_message`` to display the embed.

        :param name: A specific Page object name. If this is not set, the next Page in the list will be called.
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

    async def close(self) -> None:
        """Closes the active Menu instance."""
        if self.pages[self.page].buttons:
            await self._cleanup_reactions()

        self.active = False

    async def cancel(self) -> None:
        """Sends a cancelled message."""
        embed = Embed(title=self.pages[self.page].title, description='Menu selection cancelled -- no progress was saved.', color=Colour.red())
        await self.send_message(embed)
        await self.close()  # explicitly close the menu so reactive pages require less code

    async def send_message(self, embed: Embed) -> Message:
        """Edits a message if the channel is in a Guild, otherwise sends it to the current channel."""
        if isinstance(self.ctx.channel, GuildChannel):
            return await self.output.edit(embed=embed)
        return await self.ctx.send(embed=embed)

    async def add_buttons(self, ) -> None:
        for button in self.pages[self.page].buttons:
            await self.output.add_reaction(button)

    def _validate_pages(self) -> None:
        if len(self.pages) <= 1:
            raise NotEnoughPagesError('The pages list must have more than one page.')

    async def _get_reaction(self) -> Message:
        """Collects a user reaction and places it into the input attribute."""
        try:
            reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=3600, check=lambda _, u: u == self.ctx.author)
        except asyncio.TimeoutError:
            await self._timeout()

        else:
            if isinstance(reaction.emoji, (Emoji, PartialEmoji)):
                return reaction.emoji.name
            return reaction.emoji

    async def _get_input(self) -> Message:
        """Collects user input and places it into the input attribute."""
        try:
            message = await self.ctx.bot.wait_for('message', timeout=3600, check=lambda m: m.author == self.ctx.author)

        except asyncio.TimeoutError:
            await self._timeout()

        else:
            return message

    async def _is_cancelled(self) -> bool:
        """Checks input for a cancellation string. If there is a match, it calls menu.cancel() and then returns True."""
        if self.input.content in self.generic_quit:
            await self.cancel()
            return True
        return False

    async def _timeout(self) -> None:
        """Sends a timeout message."""
        embed = Embed(title=self.pages[self.page].title, description='You timed out at menu selection -- no progress was saved.', color=Colour.red())
        await self.send_message(embed)

    async def _cleanup_input(self) -> None:
        """Deletes a Discord client user message."""
        if isinstance(self.ctx.channel, GuildChannel):
            await self.input.delete(delay=self.delay)

    async def _cleanup_reactions(self) -> None:
        if isinstance(self.ctx.channel, GuildChannel):
            await self.output.clear_reactions()

    @classmethod
    def override_generic_values(cls, value_type: str, replacement: Tuple[str]) -> None:
        """Allows generic input matching values built into the Menu class to be overridden.

        :param value_type: Either 'confirm', 'deny', or 'quit'.
        :param replacement: A tuple containing strings of values that act as your generic input matches.
        """
        setattr(cls, f'generic_{value_type}', replacement)
