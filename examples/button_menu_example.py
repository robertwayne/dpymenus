"""
THIS IS A WORK IN PROGRESS EXAMPLE FOR RUNNING IN THE TEST SUITE AND DEBUGGING.
"""
import copy

from discord import Embed
from discord.ext import commands
from discord.ui import Button, View

from dpymenus import ButtonMenu, Page

forward = '⏩'
reverse = '⏪'
stop = '⏹️'


class ButtonMenuExample(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def buttons(self, ctx):
        view = View()
        btn = Button(style=2, label=forward)
        btn.callback = self.btn_next
        btn2 = Button(style=2, label=stop)
        btn2.callback = self.btn_close
        view.add_item(btn)
        view.add_item(btn2)

        view2 = View()
        view2.add_item(btn)
        btn3 = Button(style=2, label=reverse)
        btn3.callback = self.btn_reverse
        view2.add_item(btn3)
        view2.add_item(btn2)

        page1 = Page(title='Button Menu', description='Follow the arrows!')
        page1.add_field(name='Example A', value='Example B')
        # page1.buttons([forward, stop]).on_next(self.first)
        page1.set_view(view)

        page2 = Page(title='Button Menu', description='So many buttons! What do they do?')
        page2.add_field(name='Example C', value='Example D')
        # page2.buttons([reverse, stop, forward]).on_next(self.second)
        page2.set_view(view2)

        page3 = Embed(title='Button Menu', description='We reached the end!')
        page3.add_field(name='Example E', value='Example F')

        self.menu = ButtonMenu(ctx).add_pages([page1, page2, page3])
        await self.menu.open()

    async def btn_next(self, interaction):
        await self.menu.next()

    async def btn_close(self, interaction):
        await self.menu.close()

    async def btn_reverse(self, interaction):
        await self.menu.previous()


def setup(client):
    client.add_cog(ButtonMenuExample(client))
