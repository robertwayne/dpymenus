from discord.ext import commands

from dpymenus import Page, PaginatedMenu, TextMenu


class MyChainedMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def chaining(self, ctx):
        raise NotImplementedError


def setup(client):
    client.add_cog(MyChainedMenu(client))
