from discord.ext import commands

from dpymenus import Page, PaginatedMenu


class ThirdPaginatedMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def paginated3(self, ctx, page: int = 0):
        e1 = Page(title='Page 1', description='First page test!')
        e1.add_field(name='Example A', value='Example B')

        e2 = Page(title='Page 2', description='Second page test!')
        e2.add_field(name='Example C', value='Example D')

        e3 = Page(title='Page 3', description='Third page test!')
        e3.add_field(name='Example E', value='Example F')

        menu = PaginatedMenu(ctx)
        menu.add_pages([e1, e2, e3])
        menu.set_initial_page(max(0, page - 1))  # this is a very naive way to handle a user-friendly 1-based index
        await menu.open()

    @commands.command()
    async def paginated4(self, ctx, page: str = None):
        """This alternate example will show how to use strings instead of page numbers; for example, users can
        jump to a specific section of your help menu via the page mapping below. Try with `!paginated4 mod` to
        see it in action. There are other ways to design this, but a simple dictionary mapping is probably enough
        for most use cases."""
        e1 = Page(title='User Help', description='User help page test!')
        e1.add_field(name='Example A', value='Example B')

        e2 = Page(title='Mod Help', description='Mod help page test!')
        e2.add_field(name='Example C', value='Example D')

        e3 = Page(title='Admin Help', description='Admin help page test!')
        e3.add_field(name='Example E', value='Example F')

        page_map = {None: e1, 'user': e1, 'mod': e2, 'admin': e3}

        menu = PaginatedMenu(ctx)
        menu.add_pages([e1, e2, e3])
        menu.set_initial_page(page_map[page].index)
        await menu.open()


def setup(client):
    client.add_cog(ThirdPaginatedMenu(client))
