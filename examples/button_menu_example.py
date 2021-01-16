from discord import Embed
from discord.ext import commands

from dpymenus import ButtonMenu, Page

forward = "⏩"
reverse = "⏪"
stop = "⏹️"


class MyButtonMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def buttons(self, ctx):
        page1 = Page(title="Button Menu", description="Follow the arrows!")
        page1.add_field(name="Example A", value="Example B")
        page1.buttons([forward, stop]).on_next(self.first)

        page2 = Page(title="Button Menu", description="So many buttons! What do they do?")
        page2.add_field(name="Example C", value="Example D")
        page2.buttons([reverse, stop, forward]).on_next(self.second)

        page3 = Embed(title="Button Menu", description="We reached the end!")
        page3.add_field(name="Example E", value="Example F")

        menu = ButtonMenu(ctx).add_pages([page1, page2, page3])
        await menu.open()

    @staticmethod
    async def first(menu):
        if menu.button_pressed(forward):
            await menu.next()

        elif menu.button_pressed(stop):
            await menu.close()

    @staticmethod
    async def second(menu):
        if menu.button_pressed(reverse):
            await menu.go_to("first")

        elif menu.button_pressed(forward):
            await menu.next()

        elif menu.button_pressed(stop):
            await menu.close()


def setup(client):
    client.add_cog(MyButtonMenu(client))
