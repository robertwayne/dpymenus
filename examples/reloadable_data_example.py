from random import randint

from discord.ext import commands

from dpymenus import Page, ButtonMenu


class MyButtonMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def random(self, ctx):
        reload = "🔄"
        close = "❌"

        async def make_request():
            return {"mock": "json", "request": "data", "random_data": randint(1, 100)}

        async def update_data(menu):
            if menu.button_pressed(reload):
                response = await make_request()

                p = Page(title="Awesome Data", description="We can reload this data.")
                p.add_field(name="Random Updating Integer", value=response.get("random_data"))
                await menu.output.edit(embed=p.as_safe_embed())

            elif menu.button_pressed(close):
                await menu.close()

        page1 = Page(title="Example", description="example")
        page1.on_next(update_data)
        page1.buttons([reload, close])

        menu = ButtonMenu(ctx)
        menu.add_pages([page1])
        await menu.open()


def setup(client):
    client.add_cog(MyButtonMenu(client))
