# Visit https://dpymenus.com for detailed tutorials on getting started.

from discord import Embed
from discord.ext import commands

from dpymenus import PaginatedMenu


class MyPaginatedMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def demo(self, ctx):
        e1 = Embed(title='Page 1', description='First page test!')
        e1.add_field(name='Example A', value='Example B')

        e2 = Embed(title='Page 2', description='Second page test!')
        e2.add_field(name='Example C', value='Example D')

        e3 = Embed(title='Page 3', description='Third page test!')
        e3.add_field(name='Example E', value='Example F')

        cancel = Embed(title='Cancel Page', description='Cancel page test.')
        cancel.add_field(name='Example E', value='Example F')

        timeout = Embed(title='Timeout Page', description='Timeout page test.')
        timeout.add_field(name='Example E', value='Example F')

        menu = PaginatedMenu(ctx)
        menu.add_pages([e1, e2, e3])
        menu.set_timeout(10)
        await menu.open()

        # You can also do fluent-style chaining on the menu methods; similar to a discord.py Embed. For example...
        #
        # menu = (PaginatedMenu(ctx)
        #         .set_timeout(5)
        #         .add_pages([page1, page2, page3, page4])
        #         .show_skip_buttons()
        #         .hide_cancel_button()
        #         )
        # await menu.open()
        #
        # ...or...
        #
        # menu = PaginatedMenu(ctx).add_pages([e1, e2, e3]).set_cancel_page(cancel).set_timeout_page(timeout).set_timeout(20)
        # await menu.open()


def setup(client):
    client.add_cog(MyPaginatedMenu(client))
