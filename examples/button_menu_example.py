from discord import Colour
from discord.ext import commands

from dpymenus import ButtonMenu

forward = '⏩'
reverse = '⏪'
stop = '⏹️'


class MyButtonMenu(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def buttons(self, ctx: commands.Context):
        menu = ButtonMenu(ctx)

        await menu.add_page(title='Button Menu', description='Follow the arrows!', color=Colour.red(),
                            on_next=self.first, buttons=[forward, stop])

        await menu.add_page(title='Button Menu', description='So many buttons! What do they do?', color=Colour.orange(),
                            on_next=self.second, buttons=[reverse, forward, stop])

        await menu.add_page(title='Button Menu', description='We reached the end!', color=Colour.green())

        await menu.open()

    @staticmethod
    async def first(m: ButtonMenu):
        if m.input == forward:
            await m.next()

        elif m.input == stop:
            await m.cancel()

    @staticmethod
    async def second(m: ButtonMenu):
        if m.input == reverse:
            await m.next('first')  # we can pass in the name of a callback function (on_next) to go to that page

        elif m.input == forward:
            await m.next()

        elif m.input == stop:
            await m.cancel()


def setup(client: commands.Bot):
    client.add_cog(MyButtonMenu(client))
