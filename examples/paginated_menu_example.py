from discord import Embed
from discord.ext import commands

# Make sure you import the type of menu you plan on using.
from dpymenus import PaginatedMenu


class MyButtonMenu(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def buttons(self, ctx: commands.Context):
        # We start my instantiating a menu object. In this case, we're using `PaginatedMenu`. We have to pass our command context.
        menu = PaginatedMenu(ctx)

        # In this example, we're going to start by defining a few embeds. If you have used `discord.py` before, this should be
        # familiar syntax and is the idiomatic way to construct new embeds in the library. We will create three of them, one
        # for each page of the menu.
        e1 = Embed(title='Page 1', description='First page test!')
        e1.add_field(name='Example A', value='Example B')

        e2 = Embed(title='Page 2', description='Second page test!')
        e1.add_field(name='Example C', value='Example D')

        e3 = Embed(title='Page 3', description='Third page test!')
        e1.add_field(name='Example E', value='Example F')

        # Next we will add these pages using the `add_pages` method. This method will take a list of `Embed` objects,
        # where each `Embed` should include an `embed` pointing to one of the previously created embeds.
        await menu.add_pages([e1, e2, e3])

        # Finally we can use the `open()` method on our menu object to start the menu loop.
        await menu.open()


def setup(client: commands.Bot):
    client.add_cog(MyButtonMenu(client))
