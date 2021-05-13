import time
from operator import itemgetter
from typing import List, TYPE_CHECKING

from dpymenus import sessions
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
        if len(sessions[self.key]) == 0:
            del sessions[self.key]

    def kill_or_freeze(self):
        """Kills or freezes a session based on user defined settings."""
        self.freeze() if ALLOW_SESSION_RESTORE else self.kill()

    @staticmethod
    def get(instance: 'Menu') -> 'Session':
        """Returns an existing session object from the sessions store."""
        if user_sessions := sessions.get(instance.ctx.author.id, {}):
            return user_sessions.get(instance._id, {})
        return user_sessions

    @staticmethod
    def check_user_limit(user_id):
        """Predicate check for the amount of sessions a user has total."""
        return True if len(sessions.get(user_id)) >= SESSION_PER_USER_LIMIT else False

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
        _ = Session.get(instance)

        if instance.ctx.author.id in sessions:
            if Session.check_user_limit(instance.ctx.author.id):
                earliest = min(sessions[instance.ctx.author.id].items(), key=itemgetter(0))
                await earliest[1].instance.close()
            else:
                pass

        self = Session()

        self.key = instance.ctx.author.id
        instance._id = int(time.time())
        self.instance = instance
        self.history = instance.history
        self.active = True

        if sessions.get(self.key, False):
            sessions[self.key][instance._id] = self
        else:
            sessions[self.key] = {}
            sessions[self.key][instance._id] = self

        return self
