import discord
from discord.abc import GuildChannel

from dpymenus.base_menu import BaseMenu
import asyncio
from typing import Dict, List, Optional, Set

from discord import Emoji, Message, PartialEmoji
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus.base_menu import BaseMenu
from dpymenus.button_menu import ButtonMenu
from dpymenus.page import Page


class Poll(ButtonMenu):
    """Represents a button-based response menu.

    A ButtonMenu is a composable, dynamically generated object that contains state information for a user-interactable menu.
    It contains Page objects which represent new Menu states that call methods for validation and handling.

    Attributes:
        ctx: A reference to the command Context.
        pages: A list containing references to Page objects.
        timeout: How long (in seconds) before the poll ends.
        voted: Dictionary that tracks users who have already voted.
    """

    def __init__(self, ctx: Context, pages: List[Page], timeout: int = 300):
        super().__init__(ctx, pages, timeout)
        self.voted: Set = set()
        await self._set_state_fields()

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, active={self.active} page={self.page},' \
               f'state_fields={self.state_fields}>'

    async def run(self):
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        self.output = await self.ctx.send(embed=self.pages[self.page])
        await self.add_buttons()

        while self.active:
            _loop = asyncio.get_event_loop()
            _loop.create_task(self.process_vote())

    async def validate_vote(self):
        return True if self.ctx.author not in self.voted else False

    async def _set_state_fields(self):
        for button in self.pages[self.page].buttons:
            self.state_fields.update({button: 0})
        print(self.state_fields)

    async def process_vote(self):
        try:
            await self.ctx.bot.wait_for('reaction_add', timeout=self.timeout, check=lambda u: u not in self.voted)
        except asyncio.TimeoutError:
            await self._timeout()
        else:
            for k, v in self.state_fields.items():
                print('adding on button press')
                if k == self.input.content:
                    k[v] += 1
