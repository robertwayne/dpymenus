from typing import Optional, TYPE_CHECKING

from discord.ext.commands import Context

from dpymenus import sessions

if TYPE_CHECKING:
    from dpymenus.types import Menu


class Session:
    def __init__(self, instance: "Menu"):
        self.instance = instance
        self.owner = instance.ctx.author.id

        sessions.update({(self.owner, self.instance.ctx.channel.id): self})

    def __repr__(self):
        return f'Session({self.instance})'

    def kill(self):
        """Removes a session object from the sessions store & sets it as inactive."""
        try:
            del sessions[(self.owner, self.instance.ctx.channel.id)]
            self.instance.active = False
        except KeyError:
            return

    @staticmethod
    def from_context(ctx: Context) -> "Session":
        """Gets an existing session object from the sessions store."""
        return sessions.get((ctx.author.id, ctx.channel.id))
