import asyncio
import logging
from typing import Callable, List, Optional, TYPE_CHECKING

from discord import (
    Embed,
    Emoji,
    Message,
    RawReactionActionEvent,
    Reaction,
)
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import ButtonMenu, ButtonsError, Page, PagesError, SessionError
from dpymenus.constants import GENERIC_BUTTONS
from dpymenus.hooks import call_hook
from dpymenus.settings import BUTTON_DELAY

if TYPE_CHECKING:
    from dpymenus.types import PageType, Button


class PaginatedMenu(ButtonMenu):
    """Represents an paginated, button-based response menu."""

    _cancel_page: Optional['PageType']
    _timeout_page: Optional['PageType']
    _skip_buttons: bool
    _cancel_button: bool
    _buttons_list: List

    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def __repr__(self):
        return f'PaginatedMenu(active: {self.active}, pages: {self.pages}, page: {self.page}, history: {self.history})'

    @property
    def cancel_page(self) -> Optional['PageType']:
        return getattr(self, '_cancel_page', None)

    def set_cancel_page(self, embed: Embed) -> 'PaginatedMenu':
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style
        chaining.

        :param embed: Defines which page to display.
        :rtype: :class:`PaginatedMenu`
        """
        self._cancel_page = embed

        return self

    @property
    def timeout_page(self) -> Optional['PageType']:
        return getattr(self, '_timeout_page', None)

    def set_timeout_page(self, embed: Embed) -> 'PaginatedMenu':
        """Sets the function that will be called when a menu is cancelled. Returns itself for fluent-style chaining.

        :param embed: Defines which page to display.
        :rtype: :class:`PaginatedMenu`
        """
        setattr(self, '_timeout_page', embed)

        return self

    @property
    def skip_buttons(self) -> bool:
        return getattr(self, '_skip_buttons', False)

    def show_skip_buttons(self) -> 'PaginatedMenu':
        """Adds two extra buttons for jumping to the first and last page. Returns itself for fluent-style chaining.

        :rtype: :class:`PaginatedMenu`
        """
        setattr(self, '_skip_buttons', True)

        return self

    @property
    def cancel_button(self) -> bool:
        return getattr(self, '_cancel_button', True)

    def hide_cancel_button(self) -> 'PaginatedMenu':
        """Sets whether to show the cancel button or not. Returns itself for fluent-style chaining.

        :rtype: :class:`PaginatedMenu`
        """
        setattr(self, '_cancel_button', True)

        return self

    @property
    def buttons_list(self) -> List:
        return getattr(self, '_buttons_list', [])

    def buttons(self, buttons: List['Button']) -> 'PaginatedMenu':
        """Replaces the default buttons. You must include 3 or 5 emoji/strings in the order they would be displayed.
        0 and 5 are only shown if `enable_skip_buttons` is set, otherwise 2, 3, and 4 will be shown.

        You can pass in `None` or an empty string for 0 and 5 if you do not intend on using them. If you only pass in 3 values, they
        will be filled in as the defaults for you. If you enable the skip buttons without having values set, it will
        use those defaults.

        Returns itself for fluent-style chaining.

        :param buttons: Which emoji reactions will replace the default buttons.
        :rtype: :class:`PaginatedMenu`
        """
        _buttons = buttons

        if len(_buttons) < 3:
            _buttons.insert(0, GENERIC_BUTTONS[0])
            _buttons.insert(4, GENERIC_BUTTONS[4])

        setattr(self, '_buttons_list', _buttons)

        return self

    async def send_message(self, page: 'PageType'):
        """Updates the output message. We override the base implementation because we always want to edit,
        even in a DM  channel type.

        :param page: A :class:`PageType` to send to Discord.
        """
        safe_embed = page.as_safe_embed() if type(page) == Page else page

        await self.output.edit(embed=safe_embed)

    async def open(self):
        """The entry point to a new PaginatedMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        try:
            if len(self.buttons_list) == 0:
                self.buttons(GENERIC_BUTTONS)

            self._validate_buttons()
            await super()._open()

        except (ButtonsError, PagesError) as exc:
            logging.error(exc.message)

        except SessionError as exc:
            logging.info(exc.message)

        else:
            await self._add_buttons()

            # refresh our message content with the reactions added
            self.output = await self.destination.fetch_message(self.output.id)

            await call_hook(self, '_hook_after_open')

            while self.active:
                await call_hook(self, '_hook_before_update')
                self.input = await self._get_input()

                # this will be true when input handles a timeout event
                if (not self.output) or (not self.active) or (self.output and self.persist and not self.active):
                    return

                if self.output and isinstance(self.output.channel, GuildChannel):
                    await self.output.remove_reaction(self.input, self.ctx.author)

                # this must come after removing reactions to prevent duplicate actions on bot remove
                await self._handle_transition()

            await self._safe_clear_reactions()

    # Internal Methods
    async def _get_input(self) -> Optional[Message]:
        """Waits for a user reaction input event and returns the message object."""
        tasks = [
            asyncio.create_task(task())
            for task in [self._get_reaction_add, self._get_reaction_remove, self._shortcircuit]
        ]

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=self.timeout)

        if not self.active:
            self.kill_tasks(pending)
            return

        # if all tasks are still pending, we force a timeout by manually calling cleanup methods
        if len(pending) == len(tasks):
            await self._timeout_menu()
        else:
            for future in done:
                result = future.result()
                if result:
                    return result
                else:
                    return

        self.kill_tasks(pending)

    def _get_check(self) -> Callable:
        """Returns a check predicate based on detected buttons. Using the standard button list uses a
        simpler, and faster, predicate. Using custom buttons has to iterate over buttons to ensure they
        are valid options, thus slower. Likely not large enough to notice in practice, but care should be
        taken nonetheless."""
        check = self._check_reaction_defaults

        if self.custom_check:
            check = self.custom_check
        elif self.buttons_list != GENERIC_BUTTONS:
            check = self._check

        return check

    async def _get_reaction_add(self) -> Optional['Button']:
        """Waits for a user reaction add event and returns the event object."""
        check = self._get_check()
        reaction_event = await self.ctx.bot.wait_for('raw_reaction_add', check=check)
        return reaction_event.emoji

    async def _get_reaction_remove(self) -> Optional['Button']:
        """Waits for a user reaction remove event and returns the event object."""
        check = self._get_check()
        reaction_event = await self.ctx.bot.wait_for('raw_reaction_remove', check=check)
        return reaction_event.emoji

    def _check_reaction_defaults(self, event: RawReactionActionEvent) -> bool:
        """Returns true if the event author is the same as the initial value in the menu context. This function
        specifically checks against the default button list (GENERIC_BUTTONS)."""
        return (
            event.user_id == self.ctx.author.id
            and event.message_id == self.output.id
            and any(event.emoji.name == btn for btn in self.buttons_list)
        )

    def _validate_buttons(self):
        """Checks that the menu was passed the appropriate amount of buttons."""
        if self.buttons_list != GENERIC_BUTTONS:
            if len(self.buttons_list) != 3 and len(self.buttons_list) != 5:
                raise ButtonsError(f'Buttons length mismatch. Expected 3 or 5, found {len(self.buttons_list)}')

    async def _add_buttons(self):
        """Adds reactions to the message object based on what was passed into the page buttons. Handles the cancel
        and skip button settings."""
        if self.cancel_button is False:
            self.buttons_list[2] = None

        if self.skip_buttons:
            for button in self.buttons_list:
                if button is None:
                    continue
                await self.output.add_reaction(button)
                await asyncio.sleep(BUTTON_DELAY)
        else:
            for button in self.buttons_list[1:4]:
                if button is None:
                    continue

                await self.output.add_reaction(button)
                await asyncio.sleep(BUTTON_DELAY)

    async def _handle_transition(self):
        """Dictionary mapping of reactions to methods to be called when handling user input on a button."""
        transitions = [
            self.to_first,
            self.previous,
            self.close,
            self.next,
            self.to_last,
        ]

        if self.cancel_button is False:
            transitions.remove(self.close)

        if self.skip_buttons is False:
            transitions.remove(self.to_first)
            transitions.remove(self.to_last)

        transition_map = {
            (button.emoji.name if isinstance(button.emoji, Emoji) else button.emoji)
            if isinstance(button, Reaction)
            else button: transition
            for button, transition in zip(self.output.reactions, transitions)
        }

        if not transition_map[self.input.name] == self.close:
            await call_hook(self, '_hook_after_update')

        await transition_map[self.input.name]()
