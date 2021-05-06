from discord.ext import commands

from dpymenus import Page, PaginatedMenu


class MySQLitePaginatedMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def sqlite2(self, ctx):
        raise NotImplementedError


def setup(client):
    client.add_cog(MySQLitePaginatedMenu(client))
