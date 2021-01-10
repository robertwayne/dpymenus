import logging
from typing import Dict, List, Union

from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import BaseMenu
from dpymenus.constants import QUIT
from dpymenus.exceptions import SessionError


class TextMenu(BaseMenu):
    """
    Represents a text-based response menu.

    :param ctx: A reference to the command context.
    """

    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def __repr__(self):
        return f'TextMenu(pages={[p.__str__() for p in self.pages]}, page={self.page}, timeout={self.timeout}, data={self.data})'

    @property
    def delay(self) -> float:
        return getattr(self, '_delay', 0.250)

    def set_delay(self, delay: float) -> 'TextMenu':
        """Sets the delay on when a users message will be deleted in guild channels. Returns itself for fluent-style chaining."""
        self._delay = delay

        return self

    @property
    def data(self) -> Dict:
        return getattr(self, '_data', {})

    def set_data(self, data: Dict) -> 'TextMenu':
        """Sets a dictionary up for persistent state data. Returns itself for fluent-style chaining."""
        self._data = data

        return self

    @property
    def normalized(self) -> bool:
        return getattr(self, '_normalized', False)

    def normalize_responses(self) -> 'TextMenu':
        """Strips all input data and ignores case when comparing strings with `response_is`. Returns itself for fluent-style chaining."""
        self._normalized = True

        return self

    def response_is(self, valid_response: Union[str, List[str]]) -> bool:
        """Helper method which checks if a users response is in the str or list of strings passed in."""
        response = self.input.content
        if self.normalized:
            response = ' '.join(response.lower().split())

        return any(response == res for res in valid_response) if isinstance(valid_response, List) else valid_response == response

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        try:
            await super()._open()
        except SessionError as exc:
            logging.info(exc.message)
        else:
            first_iter = True
            while self.active:
                if not first_iter and self.page.on_fail_event:
                    return await self.page.on_fail_event()

                first_iter = False

                self.input = await self._get_input()

                if self.input:
                    await self._cleanup_input()

                    if self._is_cancelled():
                        return await self._execute_cancel()

                    await self.page.on_next_event(self)

    # Internal Methods
    async def _cleanup_input(self):
        """Deletes a Discord client user message."""
        if isinstance(self.output.channel, GuildChannel):
            await self.input.delete(delay=self.delay)

    def _is_cancelled(self) -> bool:
        """Checks input for a cancellation string. If there is a match, it calls the ``menu.cancel()`` method and returns True."""
        if self.response_is(QUIT):
            return True
        return False
