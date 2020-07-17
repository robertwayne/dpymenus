import asyncio
from typing import Dict, Set
from warnings import warn

from discord import User
from discord.ext.commands import Context

from dpymenus import ButtonMenu
from dpymenus.exceptions import ButtonsError, CallbackError, PagesError


class Poll(ButtonMenu):
    """Represents a Poll menu.

    Attributes
        :ctx: A reference to the command context.
        :timeout: How long (in seconds) before the poll ends.
        :voted: Dictionary that tracks users who have already voted.
    """

    def __init__(self, ctx: Context, timeout: int = 300):
        super().__init__(ctx, timeout)
        self.voted: Set[User] = set()

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, active={self.active} page={self.page_index},' \
               f'data={self.data}>'

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        await self._validate_pages()

        if not await super().validate_user():
            return

        await super().set_user_active()

        await self._set_data()

        self.output = await self.ctx.send(embed=self.page)
        await self._add_buttons()

        pending = set()
        while self.active:
            try:
                _, pending = await asyncio.wait([asyncio.create_task(self._get_vote_add()), asyncio.create_task(self._get_vote_remove()),
                                                 asyncio.create_task(self._poll_timer())], return_when=asyncio.FIRST_COMPLETED)
            finally:
                for task in pending:
                    task.cancel()

                await self._finish_poll()

    # Utility Methods
    async def results(self) -> Dict[str, int]:
        """Utility method to get a dictionary of poll results."""
        return {choice: len(voters) for choice, voters in self.data.items()}

    async def add_results_fields(self):
        """Utility method to add new fields to your next page automatically."""
        for choice, voters in self.data.items():
            next_page = await self.get_next_page()
            next_page.add_field(name=choice, value=str(len(voters)))

    async def generate_results_page(self):
        """Utility method to build your entire results page automatically."""
        next_page = await self.get_next_page()

        await self.add_results_fields()

        highest_value = max(self.data.values())
        winning_key = {choice for choice, voters in self.data.items() if voters == highest_value}

        if len(highest_value) == 0:
            next_page.description = ' '.join([next_page.description, f"It's a draw!"])

        else:
            next_page.description = ' '.join([next_page.description, f'{str(next(iter(winning_key)))} wins!'])

    # Internal Methods
    async def _get_vote_add(self):
        """Watches for a user adding a reaction on the Poll. Adds them to the relevant state_field values."""
        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=self.timeout, check=lambda _, u: u != self.ctx.bot.user)

            except asyncio.TimeoutError:
                return

            else:
                if reaction.emoji in self.page.buttons:
                    self.data[reaction.emoji].add(user.id)

    async def _get_vote_remove(self):
        """Watches for a user removing a reaction on the Poll. Removes them from the relevant state_field values."""
        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for('reaction_remove', timeout=self.timeout, check=lambda _, u: u != self.ctx.bot.user)

            except asyncio.TimeoutError:
                return

            else:
                if reaction.emoji in self.page.buttons:
                    self.data[reaction.emoji].remove(user.id)

    async def _poll_timer(self):
        """Handles poll duration."""
        await asyncio.sleep(self.timeout)

    async def _finish_poll(self):
        """Removes multi-votes and calls the Page on_next function when finished."""
        cheaters = await self._get_cheaters()
        for voters in self.data.values():
            voters -= cheaters

        await self.output.clear_reactions()
        await self.page.on_next(self)

    async def _get_cheaters(self) -> Set[int]:
        """Returns a set of user ID's that appear in more than one state_field value."""
        seen = set()
        repeated = set()
        for voters in self.data.values():
            for voter in voters:
                repeated.add(voter) if voter in seen else seen.add(voter)

        return repeated

    async def _set_data(self):
        """Internally sets data field keys and values based on the current Page button properties."""
        await self._validate_buttons()

        for button in self.page.buttons:
            self.data.update({button: set()})

    async def _validate_buttons(self):
        """Checks that Poll objects always have more than two buttons."""
        if len(self.page.buttons) < 2:
            raise ButtonsError(f'A Poll primary page must have at least two buttons. Expected at least 2, found {len(self.page.buttons)}.')

    async def _validate_pages(self):
        """Checks that the Menu contains at least one Page."""
        if len(self.pages) != 2:
            raise PagesError(f'A Poll can only have two pages. Expected 2, found {len(self.pages)}.')

        if self.page.on_cancel or self.page.on_fail or self.page.on_timeout:
            raise CallbackError('A Poll can not have `on_cancel`, `on_fail`, or `on_timeout` callbacks.')

        if len(self.page.buttons) > 5:
            warn('Adding more than 5 buttons to a page at once may result in discord.py throttling the bot client.')

    @staticmethod
    async def get_voters(users: Set[User]) -> Set[User]:
        """Returns a set of user ID's."""
        return {user.id for user in users}
