import asyncio
import logging
from typing import List, Optional, TYPE_CHECKING

from discord import (Embed, Emoji, Message, RawReactionActionEvent, Reaction, )
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import ButtonMenu, Page, Session
from dpymenus.constants import GENERIC_BUTTONS
from dpymenus.exceptions import ButtonsError, PagesError, SessionError
from dpymenus.template import Template

if TYPE_CHECKING:
    from dpymenus.types import PageType, Button


class PaginatedMenu(ButtonMenu):
    """
    Represents an paginated, button-based response menu.

    :param ctx: A reference to the command context.
    """

    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def __repr__(self):
        return (
            f"PaginatedMenu(pages={[p.__str__() for p in self.pages]}, page={self.page}, timeout={self.timeout}, "
            f"skip_buttons={self.skip_buttons} page_numbers={self.page_numbers}, cancel_page={self.cancel_page}, "
            f"timeout_page={self.timeout_page})"
        )

    @property
    def cancel_page(self) -> Optional[Embed]:
        return getattr(self, "_cancel_page", None)

    def set_cancel_page(self, embed: Embed) -> "PaginatedMenu":
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style chaining."""
        self._cancel_page = embed

        return self

    @property
    def timeout_page(self) -> Optional[Embed]:
        return getattr(self, "_timeout_page", None)

    def set_timeout_page(self, embed: Embed) -> "PaginatedMenu":
        """Sets the function that will be called when the `cancel` event runs. Returns itself for fluent-style chaining."""
        self._timeout_page = embed

        return self

    @property
    def page_numbers(self) -> bool:
        return getattr(self, "_page_numbers", False)

    def show_page_numbers(self) -> "PaginatedMenu":
        """Adds page numbers to each embeds by overwriting the footer. Returns itself for fluent-style chaining."""
        self._page_numbers = True

        # check if pages were set prior to calling this method; if so, we reset footers
        if self.pages:
            for i, page in enumerate(self.pages):
                page.set_footer(text=f"{i + 1}/{len(self.pages)}")

        return self

    @property
    def skip_buttons(self) -> bool:
        return getattr(self, "_skip_buttons", False)

    def show_skip_buttons(self) -> "PaginatedMenu":
        """Adds two extra buttons for jumping to the first and last page. Returns itself for fluent-style chaining."""
        self._skip_buttons = True

        return self

    @property
    def cancel_button(self) -> bool:
        return getattr(self, "_cancel_button", True)

    def hide_cancel_button(self) -> "PaginatedMenu":
        """Sets whether to show the cancel button or not. Returns itself for fluent-style chaining."""
        self._cancel_button = False

        return self

    @property
    def buttons_list(self) -> List:
        return getattr(self, "_buttons_list", [])

    def buttons(self, buttons: List["Button"]) -> "PaginatedMenu":
        """Replaces the default buttons. You must include 3 or 5 emoji/strings in the order they would be displayed.
        0 and 5 are only shown if `enable_skip_buttons` is set, otherwise 2, 3, and 4 will be shown. You can pass in
        `None` or an empty string for 0 and 5 if you do not intend on using them. If you only pass in 3 values, they
         will be filled in as the defaults for you. If you enable the skip buttons without having values set, it will
         use those defaults."""
        self._buttons_list = buttons

        if len(buttons) == 3:
            self.buttons_list.insert(0, GENERIC_BUTTONS[0])
            self.buttons_list.insert(4, GENERIC_BUTTONS[4])

        return self

    async def open(self):
        """The entry point to a new PaginatedMenu instance; starts the main menu loop.
        Manages gathering user input, basic validation, sending messages, and cancellation requests."""
        try:
            # we have to set these here so we can validate cleanly
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

            while self.active:
                await self._handle_tasks()
                await self._handle_transition()

                if isinstance(self.output.channel, GuildChannel):
                    await self.output.remove_reaction(self.input, self.ctx.author)

            await self._cleanup_reactions()

    async def send_message(self, embed: Embed) -> Message:
        """
        Edits the menu output message. We override the :class:`~dpymenus.BaseMenu` implementation because
        we always want to edit, even in a DM channel type.

        :param embed: A Discord :py:class:`~discord.Embed` object.
        """
        return await self.output.edit(embed=embed)

    def add_pages(self, pages: List["PageType"], template: "Template" = None) -> "PaginatedMenu":
        """Helper method to convert embeds into Pages and add them to a menu."""
        self._validate_pages(pages)

        for i, page in enumerate(pages):
            if not isinstance(page, Page):
                page = Page.convert_from(page)

            page.index = i

            # very naive impl -- need to allow overrides // just a test
            page.apply_template(template)

            self.pages.append(page)

        self.page = self.pages[0]

        return self

    # Internal Methods
    async def _get_reaction_add(self) -> "Button":
        """Collects a user reaction and places it into the input attribute. Returns a :py:class:`discord.Emoji` or string."""
        reaction_event = await self.ctx.bot.wait_for(
            "raw_reaction_add",
            check=self._check_reaction if self.buttons_list != GENERIC_BUTTONS else self._check_reaction_defaults,
        )

        return reaction_event.emoji

    async def _get_reaction_remove(self) -> "Button":
        """Collects a user reaction and places it into the input attribute. Returns a :py:class:`discord.Emoji` or string."""
        reaction_event = await self.ctx.bot.wait_for(
            "raw_reaction_remove",
            check=self._check_reaction if self.buttons_list != GENERIC_BUTTONS else self._check_reaction_defaults,
        )

        return reaction_event.emoji

    def _check_reaction_defaults(self, event: RawReactionActionEvent) -> bool:
        """Returns true if the author is the person who reacted and the message ID's match. Checks the generic buttons."""
        return (
            event.user_id == self.ctx.author.id
            and event.message_id == self.output.id
            and any(event.emoji.name == btn for btn in self.buttons_list)
        )

    def _validate_buttons(self):
        if self.buttons_list != GENERIC_BUTTONS:
            if len(self.buttons_list) != 3 and len(self.buttons_list) != 5:
                raise ButtonsError(f"Buttons length mismatch. Expected 3 or 5, found {len(self.buttons_list)}")

            self._check_buttons(self.buttons_list)

    async def _add_buttons(self):
        """Adds reactions to the message object based on what was passed into the page buttons."""
        if not self.cancel_button:
            self.buttons_list[2] = None

        if self.skip_buttons:
            for button in self.buttons_list:
                if button is None:
                    continue
                await self.output.add_reaction(button)
        else:
            for button in self.buttons_list[1:4]:
                if button is None:
                    continue

                await self.output.add_reaction(button)

    async def _handle_transition(self):
        """Dictionary mapping of reactions to methods to be called when handling user input on a button."""
        transitions = [
            self.to_first,
            self.previous,
            self.close,
            self.next,
            self.to_last,
        ]

        if not self.cancel_button:
            transitions.remove(self.close)

        if not self.skip_buttons:
            transitions.remove(self.to_first)
            transitions.remove(self.to_last)

        transition_map = {
            (button.emoji.name if isinstance(button.emoji, Emoji) else button.emoji)
            if isinstance(button, Reaction)
            else button: transition
            for button, transition in zip(self.output.reactions, transitions)
        }

        await transition_map[self.input.name]()
