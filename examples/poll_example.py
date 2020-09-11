# Visit https://dpymenus.com for detailed tutorials on getting started.

import discord
from discord.ext import commands

from dpymenus import Poll


class MyPoll(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def poll(self, ctx):
        first = discord.Embed(title='Sun vs Moon Poll', description='Do you prefer the sun or the moon?')
        first.set_footer(text="Only vote once! Your vote won't count if you cheat!")

        second = discord.Embed(title='Sun vs Moon Poll', description=f'Results are in!')

        menu = Poll(ctx).set_timeout(60).add_pages([first, second])
        await menu.open()

    @staticmethod
    async def finish(menu):
        await menu.generate_results_page()
        await menu.next()


def setup(client):
    client.add_cog(MyPoll(client))
