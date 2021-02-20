from typing import TYPE_CHECKING

from discord.ext.commands import Context

from dpymenus import SessionError, sessions
from dpymenus.settings import PREVENT_MULTISESSIONS

if TYPE_CHECKING:
    from dpymenus.types import Menu, SessionKey


class Session:
    key: 'SessionKey'
    instance: 'Menu'
    owner: int

    def __repr__(self):
        return f'Session({self.instance})'

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
            if PREVENT_MULTISESSIONS is False:
                session.kill()
                await session.instance.close()
            else:
                raise SessionError(
                    f'Duplicate session in channel [{instance.ctx.channel.id}] for user [{instance.ctx.author.id}].'
                )

        self = Session()

        self.key = (instance.ctx.author.id, instance.ctx.channel.id)
        self.instance = instance
        self.owner = instance.ctx.author.id

        sessions.update({self.key: self})

        return self
