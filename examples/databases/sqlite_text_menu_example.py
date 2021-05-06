from discord.ext import commands

from dpymenus import Page, TextMenu


class MySQLiteTextMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def sqlite(self, ctx):
        raise NotImplementedError


def setup(client):
    client.add_cog(MySQLiteTextMenu(client))
