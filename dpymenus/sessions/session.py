from typing import TYPE_CHECKING

from dpymenus import sessions

if TYPE_CHECKING:
    from dpymenus.types import Menu


class Session:
    def __init__(self, instance: "Menu"):
        self.instance = instance
        self.owner = instance.author
        self.active = True

        sessions.update({(self.instance.ctx.author.id, self.instance.ctx.channel.id), instance})

    def kill(self):
        self.active = False
        del sessions[(self.instance.ctx.author.id, self.instance.ctx.channel.id)]
