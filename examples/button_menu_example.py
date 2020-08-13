from discord.ext import commands

# Make sure you import the type of menu you plan on using.
from dpymenus import ButtonMenu

# First we will define some emoji strings. We will be using these as our menu buttons. Discord will
# display these as proper emojis, and the `ButtonMenu` will automatically turn these into reactions on your
# pages (which we will create in a moment).
forward = '⏩'
reverse = '⏪'
stop = '⏹️'


class MyButtonMenu(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def buttons(self, ctx: commands.Context):
        # We start my instantiating a menu object. In this case we're using `ButtonMenu`. We have to pass our command context.
        menu = ButtonMenu(ctx)

        # Next we will create some pages using the `add_page` method. This is done the same way you would create an Embed
        # idiomatically using `discord.Embed()`, but it also takes an on_next and buttons arguments. Buttons should be a
        # list of valid Discord emojis -- these can be Emoji objects or Unicode strings. In this case, we defined the
        # emojis ahead of time within the file (so they are loaded only once), and we can reuse them easily.
        #
        # `on_next` must be a reference to a function. Remember, when you pass a reference to the function you should NOT
        # use () parenthesis at the end of the function name. That would call the function immediately, as pages were being
        # created. Instead, the reference will be called by the menu loop at a later time.
        await menu.add_page(title='Button Menu', description='Follow the arrows!',
                            on_next=self.first, buttons=[forward, stop])

        await menu.add_page(title='Button Menu', description='So many buttons! What do they do?',
                            on_next=self.second, buttons=[reverse, forward, stop])

        # Note that we didn't include an `on_next` or any `buttons` on the last `Page`. This is important as it denotes
        # this will be our final and closing page on the menu. What this means is that when you arrive at this page,
        # no matter how it was done, the menu loop will be closed and no longer respond to user input.
        await menu.add_page(title='Button Menu', description='We reached the end!')

        # Finally, after all our menu pages are constructed, we can use the `open()` method on our menu object to
        # start the menu loop.
        await menu.open()

    # Here we are defining the functions our pages reference (this is your `on_next` parameter). These should always take
    # a menu object (in this case ButtonMenu) so we can test against the input!
    @staticmethod
    async def first(m: ButtonMenu):
        # Here we will test the received input against our emojis defined above. This code is literally just checking:
        # "if the person clicked the forward emoji, we will go to the next page", and "if they clicked the stop emoji,
        # we will cancel the menu".
        #
        # `next()` and `cancel()` are both built-in methods on the menu object that do what they sound like.
        if m.input == forward:
            await m.next()

        elif m.input == stop:
            await m.cancel()

    @staticmethod
    async def second(m: ButtonMenu):
        # Here we are using the `go_to()` method. By passing in a string called 'first', we are telling the menu that the next
        # page we will go to should have an `on_next` reference called 'first'.
        #
        # Your pages are always internally referenced by the name of the function you call in their `on_next` parameters.
        if m.input == reverse:
            await m.go_to('first')

        elif m.input == forward:
            await m.next()

        elif m.input == stop:
            await m.cancel()


def setup(client: commands.Bot):
    client.add_cog(MyButtonMenu(client))
