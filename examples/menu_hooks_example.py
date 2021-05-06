from discord.ext import commands

from dpymenus import Page, PaginatedMenu, hooks


class MyHooksMenu(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.ctx = None  # we are going to track the context of each instance so we can hook in later
        self.count = 0

    @commands.command()
    async def hooks(self, ctx):
        self.ctx = ctx

        e1 = Page(title='Page 1', description='First page test!')
        e1.add_field(name='Example A', value='Example B')

        e2 = Page(title='Page 2', description='Second page test!')
        e2.add_field(name='Example C', value='Example D')

        e3 = Page(title='Page 3', description='Third page test!')
        e3.add_field(name='Example E', value='Example F')

        menu = PaginatedMenu(ctx)
        menu.add_pages([e1, e2, e3])
        menu.add_hook(hooks.BEFORE, hooks.UPDATE, self.counter)
        menu.add_hook(hooks.AFTER, hooks.CLOSE, self.show_total)
        await menu.open()

    async def counter(self):
        """This will count how many times the menu has been updated and print the value."""
        self.count += 1
        print(f'Menu updated {self.count} times.')

    async def show_total(self):
        """This will send a message in Discord chat after the menu is closed with the count."""
        await self.ctx.send(f'The menu was updated a total of {self.count} times!')


def setup(client):
    client.add_cog(MyHooksMenu(client))
