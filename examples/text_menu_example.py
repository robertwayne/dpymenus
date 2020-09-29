# Visit https://dpymenus.com for detailed tutorials on getting started.

from discord.ext import commands

from dpymenus import Page, TextMenu
from dpymenus.constants import CONFIRM


class MyTextMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx) -> None:

        page1 = Page(title='Ping Menu', description='Are you absolutely sure you want to send a ping command?')
        page1.set_footer(text='Type `yes` if you are sure.\nType `quit` to cancel this menu.')
        page1.on_next(self.confirm)

        page2 = Page(title='Ping Menu', description='Pong!')

        menu = TextMenu(ctx)
        menu.add_pages([page1, page2])
        menu.normalize_responses()
        await menu.open()

    @staticmethod
    async def confirm(menu) -> None:
        if menu.response_is(CONFIRM):
            await menu.next()


def setup(client):
    client.add_cog(MyTextMenu(client))

