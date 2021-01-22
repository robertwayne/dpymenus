import asyncio
import logging
from typing import Dict, Optional, TypeVar

import emoji
from discord import Emoji, PartialEmoji, RawReactionActionEvent, Reaction
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import BaseMenu
from dpymenus.exceptions import ButtonsError, EventError, SessionError

Button = TypeVar('Button', Emoji, PartialEmoji, str)


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
        """Sets a dictionary up for persistent state data. Returns itself for fluent-style chaining."""
        self._data = data

        return self

    def button_pressed(self, button: Button) -> bool:
        """Helper method which checks if the button the user pressed is the button passed in."""
        return button == self.input

    async def open(self):
        """The entry point to a new ButtonMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        try:
            self._validate_buttons()
            await super()._open()

        except (ButtonsError, EventError) as exc:
            logging.error(exc.message)

        except SessionError as exc:
            logging.info(exc.message)

        else:
            await self._add_buttons()
            _first_iter = True

            while self.active:
                if not _first_iter and self.last_visited_page() != self.page.index:
                    await self._add_buttons()

                elif not _first_iter and self.last_visited_page() == self.page.index:
                    if isinstance(self.output.channel, GuildChannel):
                        await self.output.remove_reaction(self.input, self.ctx.author)

                # refresh our message content with the reactions added
                self.output = await self.destination.fetch_message(self.output.id)

                self.input = await self._get_reaction_add()

                await self.page.on_next_event(self)

                if self.last_visited_page() != self.page.index:
                    await self._cleanup_reactions()

                _first_iter = False

    # Internal Methods
    async def _add_buttons(self):
        """Adds reactions to the message object based on what was passed into the page buttons."""
        for button in self.page.buttons_list:
            await self.output.add_reaction(button)

    async def _get_reaction_add(self) -> Optional[Button]:
        """Collects a user reaction and places it into the input attribute. Returns a :py:class:`discord.Emoji` or string."""
        try:
            reaction_event = await self.ctx.bot.wait_for('raw_reaction_add', timeout=self.timeout, check=self._check_reaction)

        except asyncio.TimeoutError:
            await self._execute_timeout()

        else:
            for btn in self.page.buttons_list:
                if isinstance(btn, Emoji):
                    if btn == reaction_event.emoji:
                        return btn

                elif isinstance(btn, str):
                    # split the str and test if the value between ':' is the same as the PartialEmoji name
                    _test = btn.split(':')
                    if len(_test) > 1:
                        if _test[1] == reaction_event.emoji.name:
                            return btn

                    else:
                        if btn == reaction_event.emoji.name:
                            return btn

                else:
                    return reaction_event.emoji

    async def _cleanup_reactions(self):
        """Removes all reactions from the output message object."""
        if self.output and isinstance(self.output.channel, GuildChannel):
            await self.output.clear_reactions()

    def _check_reaction(self, event: RawReactionActionEvent) -> bool:
        """Returns true if the author is the person who reacted and the message ID's match. Checks the pages buttons."""
        # cursed code, not sure how else to cover all cases though; watch for performance issues
        return (event.user_id == self.ctx.author.id
                and event.message_id == self.output.id
                and any(event.emoji.name == btn
                        for btn in [(reaction.emoji.name if isinstance(reaction.emoji, Emoji) else reaction.emoji)
                                    if isinstance(reaction, Reaction) else reaction
                                    for reaction in self.output.reactions]))

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

            self._check_buttons(page.buttons_list)

        if self.page.on_fail_event:
            raise EventError('A ButtonMenu can not capture an `on_fail` event.')

        if _cb_count < len(self.pages) - 1:
            raise EventError(f'ButtonMenu missing `on_next` captures. Expected {len(self.pages) - 1}, found {_cb_count}.')

    def _check_buttons(self, buttons_list):
        for button in buttons_list:
            if isinstance(button, (Emoji, PartialEmoji)):
                continue

            if isinstance(button, str):
                # split the str and test if the value between ':' is in the bot list
                _test = button.split(':')
                if len(_test) > 1:
                    if _test[1] in [e.name for e in self.ctx.bot.emojis]:
                        continue

                # check by key; faster than iterating over the list w/ for loop
                _test = emoji.UNICODE_EMOJI_ALIAS.get(button, None)
                if _test:
                    continue

            raise ButtonsError(f'Invalid Emoji or unicode string: {button}')
