from discord import Embed
from discord.ext import commands

from dpymenus import PaginatedMenu
from dpymenus.hooks import before, after


class MyPaginatedMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def demo(self, ctx):
        e1 = Embed(title="Page 1", description="First page test!")
        e1.add_field(name="Example A", value="Example B")

        e2 = Embed(title="Page 2", description="Second page test!")
        e2.add_field(name="Example C", value="Example D")

        e3 = Embed(title="Page 3", description="Third page test!")
        e3.add_field(name="Example E", value="Example F")

        menu = PaginatedMenu(ctx)
        menu.add_pages([e1, e2, e3])
        await menu.open()

    @before('OPEN')
    async def my_hook(self):
        print('This runs before the menu opens!')

    @after('UPDATE')
    async def my_update_hook(self):
        print('This runs after a menu update!')


def setup(client):
    client.add_cog(MyPaginatedMenu(client))
