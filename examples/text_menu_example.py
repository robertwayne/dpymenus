from discord.ext import commands
from discord.colour import Colour

from dpymenus import TextMenu


class Ping(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        menu = TextMenu(ctx)

        await menu.add_page(title='Ping Menu', color=Colour.red(), callback=self.confirm,
                            description='Are you absolutely sure you want to send a ping command?\n\n'
                                        'Type `yes` if you are sure.\nType `quit` to cancel this menu.')

        await menu.add_page(title='Ping Menu', color=Colour.green(), description='Pong!')

        await menu.open()

    @staticmethod
    async def confirm(m: TextMenu) -> None:
        if m.input.content in m.generic_confirm:  # we check if the user types in a variation of 'yes'
            await m.next()  # we go to the next page, which happens to be our finaly page (because it has no callback)


def setup(client: commands.Bot):
    client.add_cog(Ping(client))
