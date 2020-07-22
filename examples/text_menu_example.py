from discord.colour import Colour
from discord.ext import commands

# Make sure you import the type of menu you plan on using.
from dpymenus import TextMenu

# Here we are also going to use predefined text answers from the constants module.
from dpymenus.constants import CONFIRM


class Ping(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        # We start my instantiating a menu object. In this case we're using `TextMenu`. We have to pass our command context.
        menu = TextMenu(ctx)

        # Next we will create some pages using the `add_page` method. This is done the same way you would create an Embed
        # idiomatically using `discord.Embed()`, but it also takes an on_next argument. on_next must be a reference to a function.
        #
        # Remember, when you pass a reference to the function you should NOT use () parenthesis at the end of the function name.
        # That would call the function immediately, as pages were being created. Instead, the reference will be called by the menu
        # loop at a later time.
        await menu.add_page(title='Ping Menu', color=Colour.red(), on_next=self.confirm,
                            description='Are you absolutely sure you want to send a ping command?\n\n'
                                        'Type `yes` if you are sure.\nType `quit` to cancel this menu.')

        # Note that we didn't include an `on_next` on this `Page`. This is important as it denotes this will be our final and
        # closing page on the menu. What this means is that when you arrive at this page, no matter how it was done,
        # the menu loop will be closed and no longer respond to user input.
        await menu.add_page(title='Ping Menu', color=Colour.green(), description='Pong!')

        # Finally, after all our menu pages are constructed, we can use the `open()` method on our menu object to
        # start the menu loop.
        await menu.open()

    # Here we are defining the functions our pages reference (this is your `on_next` parameter). These should always take
    # a menu object (in this case ButtonMenu) so we can test against the input!
    @staticmethod
    async def confirm(m: TextMenu) -> None:
        # CONFIRM = ('y', 'yes', 'ok', 'k', 'kk', 'ready', 'rdy', 'r', 'confirm', 'okay')
        #
        # Here we will test the received input against the predfined constants. This code is literally just checking:
        # "if the person typed a word from the list CONFIRM, we move on". A `TextMenu` will also automatically perform
        # cancellation checking. If a user were to type 'quit' or 'c', the menu would close out.
        #
        # `next()` is a built-in method on the menu object that does what it sounds like -- moves to the next page.
        if m.input.content in CONFIRM:
            await m.next()


def setup(client: commands.Bot):
    client.add_cog(Ping(client))
