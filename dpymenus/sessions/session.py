from typing import TYPE_CHECKING, List

from discord.ext.commands import Context

from dpymenus import SessionError, sessions
from dpymenus.settings import ALLOW_SESSION_RESTORE, SESSION_PER_USER_LIMIT

if TYPE_CHECKING:
    from dpymenus.types import Menu, SessionKey


class Session:
    key: 'SessionKey'
    instance: 'Menu'
    history: List[int]
    active: bool

    def __repr__(self):
        return f'key={self.key}, instance={self.instance}, active={self.active}'

    def freeze(self):
        """Marks a session as inactive so it can be unfrozen or killed later."""
        self.active = False

    def unfreeze(self):
        """Marks a previously frozen session as active so it can be reloaded via command."""
        self.active = True

    def kill(self):
        """Removes a session object from the sessions store."""
        del sessions[self.key][self.instance._id]

    def kill_or_freeze(self):
        """Kills or freezes a session based on user defined settings."""
        self.freeze() if ALLOW_SESSION_RESTORE else self.kill()

    @staticmethod
    def get(instance: 'Menu') -> 'Session':
        """Returns an existing session object from the sessions store."""
        if user_sessions := sessions.get(instance.ctx.author.id, {}):
            return user_sessions.get(instance._id, {})
        return user_sessions

    def check_user_limit(self):
        """Predicate check for the amount of sessions a user has total."""
        return False if len(sessions.get(self.key)) >= SESSION_PER_USER_LIMIT else True

    def check_channel_limit(self):
        """Predicate check for the amount of sessions a user has in a single channel total."""
        return False if len(sessions.get(self.key)) >= SESSION_PER_USER_LIMIT else True

    def check_guild_limit(self):
        """Predicate check for the amount of sessions a user has in a single channel total."""
        return False if len(sessions.get(self.key)) >= SESSION_PER_USER_LIMIT else True

    @classmethod
    async def create(cls, instance: 'Menu') -> 'Session':
        """Creates a new session based from a menu instance and adds it to the session store. Checks for
        existing sessions in the store and handles safe deletion."""
        session = Session.get(instance)

        # this will cascade through several cases:
        # if a session exists and is active, we close it and create a new session
        # if a session exists and is inactive, we set it active and return the session
        # if no cases are true, we create a brand new session
        if session and session.key in sessions.keys():
            if session.active and ALLOW_SESSION_RESTORE:
                await session.instance.close()

                return session

            # we need to handle several cases here as well:
            # check the per_* limits, if within the range, create a new session
            # if not within limits, return an error / close earliest menu
            elif session.active and ALLOW_SESSION_RESTORE is False:
                if session.check_user_limit():
                    pass

            elif session.active is False and ALLOW_SESSION_RESTORE:
                session.active = True

                return session

        self = Session()

        self.key = instance.ctx.author.id
        instance._id = id(instance)
        self.instance = instance
        self.history = instance.history
        self.active = True

        if sessions.get(self.key, False):
            sessions[self.key][instance._id] = self
        else:
            sessions[self.key] = {}
            sessions[self.key][instance._id] = self

        return self
