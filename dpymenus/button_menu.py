import asyncio
import logging
from typing import Dict, Optional, Union

from discord import Emoji, RawReactionActionEvent
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import BaseMenu
from dpymenus.exceptions import ButtonsError, EventError, SessionError


class ButtonMenu(BaseMenu):
    """
    Represents a button-based response menu.

    :param ctx: A reference to the command context.
    """

    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def __repr__(self):
        return f'ButtonMenu(pages={[p.__str__() for p in self.pages]}, page={self.page}, timeout={self.timeout}, data={self.data})'

    @property
    def data(self) -> Dict:
        return getattr(self, '_data', {})

    def set_data(self, data: Dict) -> 'ButtonMenu':
        """Sets a dictionary up for persistant state data. Returns itself for fluent-style chaining."""
        self._data = data

        return self

    async def open(self):
        """The entry point to a new TextMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        try:
            self._validate_buttons()
            await super()._open()

        except (ButtonsError, EventError) as exc:
            logging.error(exc.message)

        except SessionError as exc:
            logging.info(exc.message)

        else:
            while self.active:
                await self._add_buttons()

                # refresh our message content with the reactions added
                self.output = await self.ctx.channel.fetch_message(self.output.id)

                self.input = await self._get_reaction_add()
                await self._cleanup_reactions()

                await self.page.on_next_event(self)

    # Internal Methods
    async def _add_buttons(self):
        """Adds reactions to the message object based on what was passed into the page buttons."""
        for button in self.page.buttons_list:
            await self.output.add_reaction(button)

    async def _get_reaction_add(self) -> Optional[Union[Emoji, str]]:
        """Collects a user reaction and places it into the input attribute. Returns a :py:class:`discord.Emoji` or string."""
        try:
            reaction_event = await self.ctx.bot.wait_for('raw_reaction_add', check=self._check_reaction)

        except asyncio.TimeoutError:
            await self._execute_timeout()

        else:
            return reaction_event.emoji

    async def _cleanup_reactions(self):
        """Removes all reactions from the output message object."""
        if isinstance(self.output.channel, GuildChannel):
            await self.output.clear_reactions()

    def _check_reaction(self, event: RawReactionActionEvent) -> bool:
        """Returns true if the author is the person who reacted and the message ID's match. Checks the pages buttons."""
        return (event.member is not None
                and event.user_id == self.ctx.author.id
                and event.message_id == self.output.id
                and event.member.bot is False
                and any(event.emoji.name == btn for btn in self.page.buttons_list))

    def _validate_buttons(self):
        """Ensures that a menu was passed the appropriate amount of buttons."""
        _cb_count = 0
        for page in self.pages:
            if not page.buttons_list:
                break

            if page.on_next_event:
                _cb_count += 1

            if len(page.buttons_list) < 1:
                raise ButtonsError('Any page with an `on_next` event capture must have at least one button.\n'
                                   f'{page} {page.title} only has {len(page.buttons_list)} buttons.')

            if len(page.buttons_list) > 5:
                logging.warning('Adding more than 5 buttons to a page at once may result in discord.py throttling the bot client.')

        if self.page.on_fail_event:
            raise EventError('A ButtonMenu can not capture an `on_fail` event.')

        if _cb_count < len(self.pages) - 1:
            raise EventError(f'ButtonMenu missing `on_next` captures. Expected {len(self.pages) - 1}, found {_cb_count}.')
