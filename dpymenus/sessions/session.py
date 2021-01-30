from typing import TYPE_CHECKING

from dpymenus import sessions

if TYPE_CHECKING:
    from dpymenus.types import Menu


class Session:
    def __init__(self, instance: "Menu"):
        self.instance = instance
        self.owner = instance.ctx.author.id
        self.active = True

        sessions.update({(self.owner, self.instance.ctx.channel.id): self})

    def __repr__(self):
        return f'Session({self.instance})'

    def kill(self):
        self.active = False
        del sessions[(self.owner, self.instance.ctx.channel.id)]
