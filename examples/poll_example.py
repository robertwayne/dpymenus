import discord
from discord.ext import commands

from dpymenus import Poll


class MyPoll(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def poll(self, ctx: commands.Context) -> None:
        menu = Poll(ctx, timeout=60)  # we set the duration of the poll to 1 minute

        first = await menu.add_page(title='Sun vs Moon Poll', description='Testing polls for dpymenus v2.0.\nDo you prefer the sun or the moon?',
                                    color=discord.Color.red(), callback=self.finish, buttons=['\U00002600', '\U0001F315'])
        first.set_footer(text="Only vote once! Your vote won't count if you cheat!")

        await menu.add_page(title='Sun vs Moon Poll', description=f'Results are in!', color=discord.Color.green())

        await menu.open()

    @staticmethod
    async def finish(m: Poll) -> None:
        await m.generate_results_page()  # we use a special utility method to generate a complete results page!
        await m.next()


def setup(client: commands.Bot):
    client.add_cog(MyPoll(client))
