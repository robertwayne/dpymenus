from discord.ext import commands

from dpymenus import Page, Poll


class MyPoll(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def poll(self, ctx):
        first = Page(title='Sun vs Moon Poll', description='Do you prefer the sun or the moon?')
        first.set_footer(text='Only vote once! Your vote won\'t count if you cheat!')
        first.buttons(['\U00002600', '\U0001F315'])
        first.on_next(self.finish)

        second = Page(title='Sun vs Moon Poll', description=f'Results are in!')

        menu = Poll(ctx).set_timeout(10).add_pages([first, second])
        await menu.open()

    @staticmethod
    async def finish(menu):
        await menu.generate_results_page()
        await menu.next()


def setup(client):
    client.add_cog(MyPoll(client))
