from discord import Colour
from discord.ext import commands

from dpymenus import ButtonMenu

forward_arrow = '\U000027A1'
back_arrow = '\U00002B05'
x_mark = '\U0000274C'


class MyButtonMenu(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def buttons(self, ctx: commands.Context):
        menu = ButtonMenu(ctx)

        await menu.add_page(title='Button Menu', description='Follow the arrows!', color=Colour.red(),
                            on_next=self.first, buttons=[forward_arrow, x_mark])

        await menu.add_page(title='Button Menu', description='So many buttons! What do they do?', color=Colour.orange(),
                            on_next=self.second, buttons=[forward_arrow, back_arrow, x_mark])

        await menu.add_page(title='Button Menu', description='We reached the end!', color=Colour.green())

        await menu.open()

    @staticmethod
    async def first(m: ButtonMenu):
        if m.input == forward_arrow:  # we move forward
            await m.next()

        elif m.input == x_mark:
            await m.cancel()

    @staticmethod
    async def second(m: ButtonMenu):
        if m.input == forward_arrow:
            await m.next()

        elif m.input == back_arrow:
            await m.next('first')  # this will take us back to the previous page

        elif m.input == x_mark:
            await m.cancel()


def setup(client: commands.Bot):
    client.add_cog(MyButtonMenu(client))
