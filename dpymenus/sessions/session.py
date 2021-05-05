from typing import TYPE_CHECKING, List

from discord.ext.commands import Context

from dpymenus import sessions
from dpymenus.settings import ALLOW_SESSION_RESTORE

if TYPE_CHECKING:
    from dpymenus.types import Menu, SessionKey


class Session:
    key: 'SessionKey'
    instance: 'Menu'
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

    def kill_or_freeze(self):
        """Kills or freezes a session based on user defined settings."""
        self.freeze() if ALLOW_SESSION_RESTORE else self.kill()

    @staticmethod
    def get(ctx: Context) -> 'Session':
        """Returns an existing session object from the sessions store."""
        return sessions.get((ctx.author.id, ctx.channel.id), None)

    @classmethod
    async def create(cls, instance: 'Menu') -> 'Session':
        """Creates a new session based from a menu instance and adds it to the session store. Checks for
        existing sessions in the store and handles safe deletion."""
        session = Session.get(instance.ctx)

        # this will cascade through several cases:
        # if a session exists and is active, we close it and create a new session
        # if a session exists and is inactive, we set it active and return the session
        # if no cases are true, we create a brand new session
        if session and session.key in sessions.keys():
            if session.active and ALLOW_SESSION_RESTORE:
                await session.instance.close()

                return session

            elif session.active is False and ALLOW_SESSION_RESTORE:
                session.active = True

                return session

        self = Session()

        self.key = (instance.ctx.author.id, instance.ctx.channel.id)
        self.instance = instance
        self.history = instance.history
        self.owner = instance.ctx.author.id
        self.active = True

        sessions.update({self.key: self})

        return self
