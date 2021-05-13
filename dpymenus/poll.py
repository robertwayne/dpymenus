import asyncio
import logging
from typing import Any, Dict, List, Set
from warnings import warn

from discord import RawReactionActionEvent, User
from discord.ext.commands import Context

from dpymenus import ButtonMenu, ButtonsError, EventError, PagesError, SessionError
from dpymenus.hooks import call_hook


class Poll(ButtonMenu):
    """Represents a Poll menu.

    :param ctx: A reference to the command context.
    """

    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.voted: Set[User] = set()

    def __repr__(self):
        return f'Poll(pages={[p.__str__() for p in self.pages]}, page={self.page.index}, timeout={self.timeout}, data={self.data})'

    # Utility Methods
    async def results(self) -> Dict[str, int]:
        """Utility method to get a dictionary of poll results."""
        return {choice: len(voters) for choice, voters in self.data.items()}

    async def add_results_fields(self):
        """Utility method to add new fields to your next page automatically."""
        for choice, voters in self.data.items():
            next_page = self.pages[self.page.index + 1]
            next_page.add_field(name=choice, value=str(len(voters)))

    async def generate_results_page(self):
        """Utility method to build your entire results page automatically."""
        next_page = self.pages[self.page.index + 1]

        await self.add_results_fields()

        highest_value = max(self.data.values())
        winning_key = {choice for choice, voters in self.data.items() if voters == highest_value}

        if len(highest_value) == 0:
            next_page.description = ' '.join([next_page.description, f'It\'s a draw!'])

        else:
            next_page.description = ' '.join([next_page.description, f'{str(next(iter(winning_key)))} wins!'])

    async def open(self):
        """The entry point to a new Poll instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        try:
            self._validate_callbacks()
            await super()._open()
        except SessionError as exc:
            logging.info(exc.message)
        else:
            await self._set_data()
            await self._add_buttons()

            await call_hook(self, '_hook_after_open')

            pending = set()
            while self.active:
                try:
                    _, pending = await asyncio.wait(
                        [
                            asyncio.create_task(self._get_vote_add()),
                            asyncio.create_task(self._get_vote_remove()),
                            asyncio.create_task(self._poll_timer()),
                        ],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                finally:
                    for task in pending:
                        task.cancel()

                    await self._finish_poll()

    # Internal Methods
    async def _get_vote_add(self):
        """Watches for a user adding a reaction on the Poll. Adds them to the relevant state_field values."""
        while True:
            try:
                reaction_event = await self.ctx.bot.wait_for(
                    'raw_reaction_add', timeout=self.timeout, check=self._check_reaction
                )

            except asyncio.TimeoutError:
                return

            else:
                if reaction_event.emoji.name in self.page.buttons_list:
                    self.data[reaction_event.emoji.name].add(reaction_event.user_id)

    async def _get_vote_remove(self):
        """Watches for a user removing a reaction on the Poll. Removes them from the relevant state_field values."""
        while True:
            try:
                reaction_event = await self.ctx.bot.wait_for(
                    'raw_reaction_remove',
                    timeout=self.timeout,
                    check=self._check_reaction,
                )

            except asyncio.TimeoutError:
                return

            else:
                if reaction_event.emoji.name in self.page.buttons_list:
                    self.data[reaction_event.emoji.name].remove(reaction_event.user_id)

    def _check_reaction(self, event: RawReactionActionEvent) -> bool:
        """Returns true only if the reaction event member is not a bot (ie. excludes self from counts)."""
        return event.member is not None and event.member.bot is False

    async def _poll_timer(self):
        """Handles poll duration."""
        await asyncio.sleep(self.timeout)

    async def _finish_poll(self):
        """Removes multi-votes and calls the Page on_next function when finished."""
        cheaters = await self._get_cheaters()
        for voters in self.data.values():
            voters -= cheaters

        await self.output.clear_reactions()
        await self.page.on_next_event(self)

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
        self._validate_buttons()

        self.set_data({})
        for button in self.page.buttons_list:
            self.data.update({button: set()})

    def _validate_buttons(self):
        """Checks that Poll objects always have more than two buttons."""
        if len(self.page.buttons_list) < 2:
            raise ButtonsError(
                f'A Poll primary page must have at least two buttons. Expected at least 2, found {len(self.page.buttons_list)}.'
            )

        if len(self.page.buttons_list) > 5:
            warn('Adding more than 5 buttons to a page at once may result in discord.py throttling the bot client.')

    @staticmethod
    def _validate_pages(pages: List[Any]):
        """Checks that the Menu contains at least one Page."""
        if len(pages) != 2:
            raise PagesError(f'A Poll can only have two pages. Expected 2, found {len(pages)}.')

    def _validate_callbacks(self):
        if self.page.on_cancel_event or self.page.on_fail_event or self.page.on_timeout_event:
            raise EventError('A Poll can not capture a `cancel`, `fail`, or `timeout` event.')

    @staticmethod
    async def get_voters(users: Set[User]) -> Set[User]:
        """Returns a set of user ID's."""
        return {user.id for user in users}
