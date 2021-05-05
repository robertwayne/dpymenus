import abc
import logging
from typing import Any, Callable, List, Optional, TYPE_CHECKING, Union

from discord import Message, Reaction, TextChannel, User
from discord.abc import GuildChannel
from discord.ext.commands import Context

from dpymenus import Page, PagesError, Session, SessionError
from dpymenus.settings import HISTORY_CACHE_LIMIT, REPLY_AS_DEFAULT

if TYPE_CHECKING:
    from dpymenus import Template
    from dpymenus.types import PageType


class BaseMenu(abc.ABC):
    """The abstract base menu object. All menu types derive from this class. Implements generic properties,
    menu loop handling, and defines various helper methods."""

    _timeout: int
    _command_message: bool
    _persist: bool
    _reply: bool
    _custom_check: Optional[Callable]
    _replies_disabled: bool

    def __init__(self, ctx: Context):
        self.ctx: Context = ctx
        self.pages: List[Page] = []
        self.page: Optional[Page] = None
        self.active: bool = True
        self.input: Optional[Union[Message, Reaction]] = None
        self.output: Optional[Message] = None
        self.history: List[int] = []

    @abc.abstractmethod
    async def open(self):
        pass

    @property
    def timeout(self) -> int:
        return getattr(self, '_timeout', 300)

    def set_timeout(self, duration: int) -> 'BaseMenu':
        """Sets the timeout on a menu. Returns itself for fluent-style chaining."""
        setattr(self, '_timeout', duration)

        return self

    @property
    def destination(self) -> Union[Context, User, TextChannel]:
        return getattr(self, '_destination', self.ctx)

    def set_destination(self, dest: Union[User, TextChannel]) -> 'BaseMenu':
        """Sets the message destination for the menu. Returns itself for fluent-style chaining."""
        setattr(self, '_destination', dest)

        return self

    @property
    def replies_disabled(self) -> bool:
        return getattr(self, '_replies_disabled', False)

    def disable_replies(self) -> 'BaseMenu':
        self._replies_disabled = True

        return self

    @property
    def command_message(self) -> bool:
        return getattr(self, '_command_message', False)

    def show_command_message(self) -> 'BaseMenu':
        """Persists user command invocation messages in the chat instead of deleting them after execution.
        Returns itself for fluent-style chaining."""
        self._command_message = True

        return self

    @property
    def persist(self) -> bool:
        return getattr(self, '_persist', False)

    def persist_on_close(self) -> 'BaseMenu':
        """Prevents message cleanup from running when a menu closes.
        Returns itself for fluent-style chaining."""
        self._persist = True

        return self

    @property
    def reply(self) -> bool:
        return getattr(self, '_reply', True)

    def use_replies(self) -> 'BaseMenu':
        """Uses the Discord reply feature on user commands.
        Returns itself for fluent-style chaining."""
        setattr(self, '_reply', True)

        return self

    @property
    def custom_check(self) -> Optional[Callable]:
        return getattr(self, '_custom_check', None)

    def set_custom_check(self, fn: Callable) -> 'BaseMenu':
        """Overrides the default check method for user responses.
        Returns itself for fluent-style chaining."""
        setattr(self, '_custom_check', fn)

        return self

    # Helper Methods
    async def close(self):
        """Gracefully exits out of the menu, performing necessary cleanup of sessions, reactions, and messages."""
        Session.get(self.ctx).kill_or_freeze()
        self.active = False

        await self._safe_delete_output()

    async def next(self):
        """Transitions to the next page."""
        if self.page.index + 1 > len(self.pages) - 1:
            return

        self.page = self.pages[self.page.index + 1]

        await self._next()

    async def previous(self):
        """Transitions to the previous page."""
        if self.page.index - 1 < 0:
            return

        self.page = self.pages[self.page.index - 1]

        await self._next()

    async def to_first(self):
        """Transitions to the first page."""
        self.page = self.pages[0]

        await self._next()

    async def to_last(self):
        """Transitions to the last page."""
        self.page = self.pages[-1:][0]

        await self._next()

    async def go_to(self, page: Optional[Union[str, int]] = None):
        """Transitions to a specific page.

        :param page: The name of the `on_next` function for a particular page or its page number. If this is not set,
        the next page in the list will be called.
        """
        if isinstance(page, int):
            self.page = self.pages[page]
        elif isinstance(page, str):
            # get a page index from its on_next callback function name and assign it
            for p in self.pages:
                if p.on_next_event.__name__ == page:
                    self.page = p
                    break

        await self._next()

    def last_visited_page(self) -> int:
        """Returns the last visited page index."""
        return self.history[-2] if len(self.history) > 1 else 0

    def add_pages(self, pages: List['PageType'], template: 'Template' = None) -> 'BaseMenu':
        """Adds a list of pages to a menu, setting their index based on the position in the list.
        Returns itself for fluent-style chaining."""
        self._validate_pages(pages)

        for i, page in enumerate(pages):
            if not isinstance(page, Page):
                page = Page.convert_from(page)

            if template:
                page = page.apply_template(template)

            page.index = i
            self.pages.append(page)

        self.page = self.pages[0]

        return self

    async def send_message(self, page: 'PageType'):
        """Updates the output message if it can be edited, otherwise sends a new message."""
        safe_embed = page.as_safe_embed() if type(page) == Page else page

        if isinstance(self.output.channel, GuildChannel):
            return await self.output.edit(embed=safe_embed)
        else:
            await self.output.delete()

        self.output = await self.destination.send(embed=safe_embed)

    # Internal Methods
    async def _open(self):
        """This method runs for ALL menus after their own open method. Session handling and initial setup is
        performed in here; it should NEVER be handled inside specific menus."""
        try:
            session = await Session.create(self)
        except SessionError as exc:
            logging.info(exc.message)
        else:
            self.history = session.history
            if self.history:
                self.page = self.pages[session.history[-1]]
            else:
                self.page = self.pages[0]

            if REPLY_AS_DEFAULT and self.replies_disabled is False:
                self.output = await self.destination.reply(embed=self.page.as_safe_embed())
            else:
                self.output = await self.destination.send(embed=self.page.as_safe_embed())

            self.input = self.ctx.message
            self._update_history()

            await self._safe_delete_input()

    async def _safe_delete_input(self):
        """Safely deletes a message if the bot has permissions and show command messages is set to false."""
        if self.command_message is False:
            try:
                await self.input.delete()
            except PermissionError:
                return

    async def _safe_delete_output(self):
        """Safely deletes a message if the bot has permissions and persist is set to false."""
        if self.persist is False:
            await self.output.delete()
            self.output = None

    def _update_history(self):
        """Adds the most recent page index to the menus history cache. If the history is longer than
        the cache limit, defined globally, then the oldest item is popped before updating the history."""
        if len(self.history) >= HISTORY_CACHE_LIMIT:
            self.history.pop(0)

        self.history.append(self.page.index)

    def _check(self, message: Message) -> bool:
        """Returns true if the event author and channel are the same as the initial values in the menu context."""
        return message.author == self.ctx.author and self.output.channel == message.channel

    async def _cancel_menu(self):
        """Closes the menu as a user-defined 'cancel' event. Checks if an on_cancel_event callback exists first."""
        if self.page.on_cancel_event:
            await self.page.on_cancel_event()
            return

        if cancel_page := getattr(self, 'cancel_page', None):
            await self.output.edit(embed=cancel_page)

        await self.close()

    async def _timeout_menu(self):
        """Closes the menu on an asyncio.TimeoutError event. If an on_timeout_event callback exists, that function
        will be run instead of the default behaviour."""
        if self.page.on_timeout_event:
            await self.page.on_timeout_event()
            return

        if timeout_page := getattr(self, 'timeout_page', None):
            await self.output.edit(embed=timeout_page)

        await self.close()

    async def _next(self):
        """Sends a message after the `next` method is called. Closes the menu instance if there is no callback for
        the on_next_event on the current page."""
        if self.__class__.__name__ != 'PaginatedMenu':
            if self.page.on_next_event is None:
                Session.get(self.ctx).kill()
                self.active = False

        self._update_history()
        await self.send_message(self.page)

    # Validation Methods
    @staticmethod
    def _validate_pages(pages: List[Any]):
        """Checks that the Menu contains at least one pages."""
        if len(pages) == 0:
            raise PagesError(f'There must be at least one page in a menu. Expected at least 1, found {len(pages)}.')
