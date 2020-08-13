from discord import Embed
from discord.ext import commands

# Make sure you import the type of menu you plan on using.
from dpymenus import PaginatedMenu


class MyButtonMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def buttons(self, ctx):
        # In this example, we're going to start by defining a few embeds. If you have used `discord.py` before, this should be
        # familiar syntax and is the idiomatic way to construct new embeds in the library. We will create five of them, three
        # for the pages in the menu, then a page for cancelling and timing out.
        e1 = Embed(title='Page 1', description='First page test!')
        e1.add_field(name='Example A', value='Example B')

        e2 = Embed(title='Page 2', description='Second page test!')
        e2.add_field(name='Example C', value='Example D')

        e3 = Embed(title='Page 3', description='Third page test!')
        e3.add_field(name='Example E', value='Example F')

        cancel = Embed(title='Cancel Page', description='Cancel page test.')
        cancel.add_field(name='Example E', value='Example F')

        timeout = Embed(title='Page 3', description='Timeout page test.')
        timeout.add_field(name='Example E', value='Example F')

        # Then we will instantiate a menu object. In this case we're using `PaginatedMenu`. We have to pass our command context.
        # We will also override the cancel and timeout defaults with our own we defined above. In addition, we will turn on page
        # numbers which will be displayed in the footer.
        menu = PaginatedMenu(ctx, page_numbers=True, on_cancel=cancel, on_timeout=timeout)

        # Next we will add these pages using the `add_pages` method. This method will take a list of `Embed` objects,
        # where each `Embed` should include an `embed` pointing to one of the previously created embeds.
        await menu.add_pages([e1, e2, e3])

        # Finally we can use the `open()` method on our menu object to start the menu loop.
        await menu.open()


def setup(client):
    client.add_cog(MyButtonMenu(client))
