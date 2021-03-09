import discord
from discord.ext import commands

from dpymenus import Page, PaginatedMenu, Template


class TemplateExample(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def templates(self, ctx):
        e1 = Page(description='First page test!')
        e1.add_field(name='Example A', value='Example B')

        e2 = Page(title='Page 2', description='Second page test!', color=discord.Color.green())
        e2.add_field(name='Example C', value='Example D')

        e3 = Page(description='Third page test!')
        e3.add_field(name='Example E', value='Example F')
        e3.set_footer(text='A defined footer overrides templates!')

        template = Template(
            title='Template Example Default Title',
            description='This is a default description!',
            color=discord.Color.blue(),
            footer='A templated footer.',
        )

        menu = PaginatedMenu(ctx)
        menu.show_command_message()
        menu.add_pages([e1, e2, e3], template=template)
        await menu.open()


def setup(client):
    client.add_cog(TemplateExample(client))
