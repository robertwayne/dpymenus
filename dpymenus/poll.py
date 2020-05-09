import asyncio
from typing import Dict, Set

from discord import User
from discord.ext.commands import Context

from dpymenus import ButtonMenu
from dpymenus.exceptions import ButtonsError, PagesError


class Poll(ButtonMenu):
    """Represents a Poll menu.

    A Poll is a composable, dynamically generated object that contains state information for a user-interactable polls.
    It contains Page objects which represent new Menu states that call methods for validation and handling.

    Attributes:
        ctx: A reference to the command Context.
        timeout: How long (in seconds) before the poll ends.
        voted: Dictionary that tracks users who have already voted.
    """

    def __init__(self, ctx: Context, timeout: int = 300):
        super().__init__(ctx, timeout)
        self.voted: Set[User] = set()

    def __repr__(self):
        return f'<Menu pages={[p.__str__() for p in self.pages]}, timeout={self.timeout}, active={self.active} page={self.page},' \
               f'state_fields={self.state_fields}>'

    async def open(self):
        """The entry point to a new Menu instance. This will start a loop until a Page object with None as its function is set.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        self._validate_pages()
        self._set_state_fields()

        self.output = await self.ctx.send(embed=self.pages[self.page])
        await self._add_buttons()

        pending = set()
        while self.active:
            try:
                done, pending = await asyncio.wait([asyncio.create_task(self._get_vote_add()), asyncio.create_task(self._get_vote_remove()),
                                                    asyncio.create_task(self._poll_timer())], return_when=asyncio.FIRST_COMPLETED)
            finally:
                for task in pending:
                    task.cancel()

                await self._finish_poll()

    # Utility Methods
    async def results(self) -> Dict[str, int]:
        """Utility method to get a dictionary of poll results."""
        return {k: len(v) for k, v in self.state_fields.items()}

    async def add_results_fields(self):
        """Utility method to add new fields to your next page automatically."""
        for k, v in self.state_fields.items():
            self.pages[self.page + 1].add_field(name=k, value=str(len(v)))

    async def generate_results_page(self):
        """Utility method to build your entire results page automatically."""
        next_page = self.pages[self.page + 1]

        await self.add_results_fields()

        highest_value = max(self.state_fields.values())
        winning_key = {key for key, value in self.state_fields.items() if value == highest_value}

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
                if reaction.emoji in self.pages[self.page].buttons:
                    self.state_fields[reaction.emoji].add(user.id)

    async def _get_vote_remove(self):
        """Watches for a user removing a reaction on the Poll. Removes them from the relevant state_field values."""
        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for('reaction_remove', timeout=self.timeout, check=lambda _, u: u != self.ctx.bot.user)

            except asyncio.TimeoutError:
                return

            else:
                if reaction.emoji in self.pages[self.page].buttons:
                    self.state_fields[reaction.emoji].remove(user.id)

    async def _poll_timer(self):
        """Handles poll duration."""
        await asyncio.sleep(self.timeout)

    async def _finish_poll(self):
        """Removes multi-votes and calls the Page callback function when finished."""
        check_cheaters = False
        for value in self.state_fields.values():
            if value:
                check_cheaters = True
                break

        if check_cheaters:
            cheaters = await self._get_cheaters()
            for voter_set in self.state_fields.values():
                voter_set -= cheaters

        await self.pages[self.page].callback(self)

    async def _get_cheaters(self) -> Set[int]:
        """Returns a set of user ID's that appear in more than one state_field value."""
        seen = set()
        repeated = set()
        for voter_set in self.state_fields.values():
            for voter in voter_set:
                if voter in seen:
                    repeated.add(voter)
                else:
                    seen.add(voter)

        return repeated

    def _set_state_fields(self):
        """Internally sets state field keys and values based on the current Page button properties."""
        self._validate_buttons()

        print(self.pages[0].buttons)
        for button in self.pages[self.page].buttons:
            self.state_fields.update({button: set()})

    def _validate_buttons(self):
        """Checks that Poll objects always have more than two buttons."""
        if len(self.pages[0].buttons) < 2:
            raise ButtonsError('A Poll primary page must have at least two buttons.')

    def _validate_pages(self):
        """Checks that the Menu contains at least one Page."""
        if len(self.pages) != 2:
            raise PagesError('A Poll can only have two pages.')

    @staticmethod
    async def get_voters(users: Set[User]) -> Set[User]:
        """Returns a set of user ID's."""
        return {user.id for user in users}
