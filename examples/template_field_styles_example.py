import discord
from discord.ext import commands

from dpymenus import FieldSort, FieldStyle, Page, PaginatedMenu, Template


class TemplateExample(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def templates2(self, ctx):
        e1 = Page(description='First page test!')

        e2 = Page(title='Page 2', description='Second page test!', color=discord.Color.green())
        e2.add_field(name='Example C', value='Example D')

        e3 = Page(description='Third page test!')
        e3.add_field(name='Example E', value='Example F')
        e3.set_footer(text='A defined footer overrides templates!')

        template = Template(
            title='Template Example Default Title',
            description='This is a default description!',
            color=discord.Color.blue(),
            footer={'text': 'This is a templated footer.'},
            fields=[
                ('Template Field A', 'Templated field description for A.', False),
                ('Template Field B', 'Templated field description for B.', True),
            ],
            field_style=FieldStyle.COMBINE,  # this will force our template fields to combine with existing fields
            field_sort=FieldSort.LAST  # our template fields will always come after existing fields
        )

        menu = PaginatedMenu(ctx)
        menu.show_command_message()
        menu.add_pages([e1, e2, e3], template=template)
        await menu.open()


def setup(client):
    client.add_cog(TemplateExample(client))
