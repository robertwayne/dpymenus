from discord import Colour, Embed
from discord.ext import commands

from dpymenus import ButtonMenu, Page

forward = '⏩'
reverse = '⏪'
stop = '⏹️'


class MyButtonMenu(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def buttons(self, ctx: commands.Context):
        menu = ButtonMenu(ctx)

        e = Embed(title='Button Menu', description='Follow the arrows!', color=Colour.red())
        e.add_field(name='test1', value='test2')

        e2 = Embed(title='Button Menu', description='So many buttons! What do they do?', color=Colour.orange())
        e2.add_field(name='Random Test', value='Stuff')

        e3 = Embed(title='Button Menu', description='We reached the end!', color=Colour.green())
        e3.add_field(name='test1', value='test2')

        await menu.add_pages([Page(embed=e, buttons=[forward, stop], on_next=self.first),
                              Page(embed=e2, buttons=[reverse, forward, stop], on_next=self.second),
                              Page(embed=e3)])

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
