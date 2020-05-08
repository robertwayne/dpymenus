import asyncio
from typing import Set

from discord import User
from discord.ext.commands import Context

from dpymenus import ButtonMenu
from dpymenus.exceptions import NoButtonsError


class Poll(ButtonMenu):
    """Represents a button-based response menu.

    A ButtonMenu is a composable, dynamically generated object that contains state information for a user-interactable menu.
    It contains Page objects which represent new Menu states that call methods for validation and handling.

    Attributes:
        ctx: A reference to the command Context.
        timeout: How long (in seconds) before the poll ends.
        voted: Dictionary that tracks users who have already voted.
    """

    def __init__(self, ctx: Context, timeout: int = 300):
        super().__init__(ctx, timeout)
        self.voted: Set[User] = set()
        self.cheaters: int = 0

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, active={self.active} page={self.page},' \
               f'state_fields={self.state_fields}>'

    async def run(self):
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        self._set_state_fields()

        self.output = await self.ctx.send(embed=self.pages[self.page])
        await self.add_buttons()

        while self.active:
            await asyncio.sleep(self.timeout)
            msg = await self.ctx.channel.fetch_message(self.output.id)
            for reaction in msg.reactions:
                if reaction.me is True:
                    users = set(await reaction.users().flatten())
                    users.remove(self.ctx.bot.user)
                    self.state_fields[reaction.emoji] = await self.valid_votes(users)

            for k, v in self.state_fields.items():
                self.state_fields[k] = max(0, v - self.cheaters)

            await self.pages[self.page].callback(self)

    async def valid_votes(self, users: Set[User]) -> int:
        count = 0
        for user in users:
            if user not in self.voted:
                count += 1
                self.voted.add(user)
            else:
                self.cheaters += 1
        return count

    async def validate_vote(self):
        return True if self.ctx.author not in self.voted else False

    def _set_state_fields(self):
        self._validate_buttons()

        for button in self.pages[self.page].buttons:
            self.state_fields.update({button: 0})

    def _validate_buttons(self):
        for page in self.pages:
            if page.callback is None:
                return

            if len(page.buttons) <= 1:
                raise NoButtonsError('A Poll primary page must have at least two buttons.')

