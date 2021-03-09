import random
from typing import List

from discord.ext import commands

from dpymenus import Page, PaginatedMenu


class SecondPaginatedMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def demo2(self, ctx):
        data = generate_list_of_random_strings()
        paginated = split_data(data, 10)  # paginate our data in chunks of 10
        pages = []

        for index, chunk in enumerate(paginated):
            page = Page(title=f'Page {index + 1} of {len(paginated)}')  # define our first page
            for item in chunk:
                page.add_field(name='Data', value=item)  # add each data point to a separate field
            pages.append(page)

        menu = PaginatedMenu(ctx)
        menu.add_pages(pages)
        await menu.open()


def setup(client):
    client.add_cog(SecondPaginatedMenu(client))


def generate_list_of_random_strings() -> List[str]:
    r = random.randint(1, 100)
    return [f'This is random data {i}.' for i in range(r)]


def split_data(data, chunk_size):
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
