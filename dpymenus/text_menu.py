import asyncio
import logging
from typing import Dict, List, Union

from discord import Message
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import PagesError, SessionError
from dpymenus.base_menu import BaseMenu
from dpymenus.constants import QUIT
from dpymenus.hooks import call_hook


class TextMenu(BaseMenu):
    """Represents a text-based response menu."""

    _delay: float
    _data: Dict
    _normalized: bool

    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def __repr__(self):
        return f'TextMenu({self.ctx})'

    @property
    def delay(self) -> float:
        return getattr(self, '_delay', 0.250)

    def set_delay(self, delay: float) -> 'TextMenu':
        """Sets the delay on when a users message will be deleted. Returns itself for fluent-style
        chaining.

        :param delay: Specifies the duration in seconds.
        :rtype: :class:`BaseMenu`
        """
        self._delay = delay

        return self

    @property
    def data(self) -> Dict:
        return getattr(self, '_data', {})

    def set_data(self, data: Dict) -> 'TextMenu':
        """Sets a dictionary up for persistent state data. Returns itself for fluent-style chaining.

        :param data: Structure representing variables that can be easily accessed across a menu instance.
        :rtype: :class:`TextMenu`
        """
        self._data = data

        return self

    @property
    def normalized(self) -> bool:
        return getattr(self, '_normalized', False)

    def normalize_responses(self) -> 'TextMenu':
        """Strips all input data and ignores case when comparing strings with `response_is`. Returns itself for
        fluent-style chaining.

        :rtype: :class:`TextMenu`
        """
        self._normalized = True

        return self

    def response_is(self, valid_response: Union[str, List[str]]) -> bool:
        """Helper method which checks if a users response is in the str or list of strings passed in.
        `response_in` exists as an alias to this method.

        :valid_response: Values to compare user input against.
        :rtype: bool
        """
        response = self.input.content
        if self.normalized:
            response = ' '.join(response.lower().split())

        return (
            any(response == res for res in valid_response)
            if isinstance(valid_response, List)
            else valid_response == response
        )

    # response_is alias
    response_in = response_is

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop. Manages gathering user input,
        basic validation, sending messages, and cancellation requests."""
        try:
            await super()._open()

        except PagesError as exc:
            logging.error(exc.message)

        except SessionError as exc:
            logging.info(exc.message)

        else:
            await call_hook(self, '_hook_after_open')

            first_iter = True

            while self.active:
                await call_hook(self, '_hook_before_update')
                if not first_iter and self.page.on_fail_event:
                    return await self.page.on_fail_event()

                self.input = await self._get_input()

                if self.input:
                    if self.output and isinstance(self.output.channel, GuildChannel) and self.delay != 0:
                        await self.input.delete(delay=self.delay)

                    if self.response_in(QUIT):
                        return await self._cancel_menu()

                    await call_hook(self, '_hook_after_update')
                    await self.page.on_next_event(self)

                first_iter = False

    # Internal Methods
    async def _get_input(self) -> Message:
        """Waits for user text input and returns the message object."""
        try:
            message = await self.ctx.bot.wait_for('message', timeout=self.timeout, check=self._check)
        except asyncio.TimeoutError:
            if self.page.on_timeout_event:
                await self.page.on_timeout_event()
            else:
                await self._timeout_menu()
        else:
            return message
