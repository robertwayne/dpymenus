from typing import TYPE_CHECKING, List

from discord.ext.commands import Context

from dpymenus import SessionError, sessions
from dpymenus.settings import PREVENT_MULTISESSIONS

if TYPE_CHECKING:
    from dpymenus.types import Menu, SessionKey


class Session:
    key: 'SessionKey'
    instance: 'Menu'
    index: int
    history: List[int]
    owner: int
    active: bool

    def __repr__(self):
        return f'key={self.key}, instance={self.instance}, owner={self.owner}, active={self.active}'

    def freeze(self):
        """Marks a session as inactive so it can be unfrozen or killed later."""
        self.active = False

    def unfreeze(self):
        """Marks a previously frozen session as active so it can be reloaded via command."""
        self.active = True

    def kill(self):
        """Removes a session object from the sessions store."""
        del sessions[(self.owner, self.instance.ctx.channel.id)]

    @staticmethod
    def get(ctx: Context) -> 'Session':
        """Returns an existing session object from the sessions store."""
        return sessions.get((ctx.author.id, ctx.channel.id), None)

    @classmethod
    async def create(cls, instance: 'Menu') -> 'Session':
        """Creates a new session based from a menu instance and adds it to the session store. Checks for
        existing sessions in the store and handles safe deletion."""
        session = Session.get(instance.ctx)

        if session and session.key in sessions.keys():
            if PREVENT_MULTISESSIONS is False and session.active:
                session.kill()
                await session.instance.close()
            else:
                if session.active is False:
                    session.active = True
                    ic(session)

                    return session
                else:
                    raise SessionError(
                        f'Duplicate session in channel [{instance.ctx.channel.id}] for user [{instance.ctx.author.id}].'
                    )

        self = Session()

        self.key = (instance.ctx.author.id, instance.ctx.channel.id)
        self.instance = instance
        self.index = instance.pages.index(instance.page)
        self.history = instance.history
        self.owner = instance.ctx.author.id
        self.active = True

        sessions.update({self.key: self})

        return self
