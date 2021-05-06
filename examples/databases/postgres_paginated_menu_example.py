from discord.ext import commands

from dpymenus import Page, PaginatedMenu


class MyPostgresPaginatedMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def postgres2(self, ctx):
        raise NotImplementedError


def setup(client):
    client.add_cog(MyPostgresPaginatedMenu(client))
