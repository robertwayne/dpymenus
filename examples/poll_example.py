from discord.ext import commands

# Make sure you import the type of menu you plan on using.
from dpymenus import Poll


class MyPoll(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def poll(self, ctx: commands.Context):
        # We start my instantiating a menu object. In this case we're using `ButtonMenu`. We have to pass our command context.
        menu = Poll(ctx, timeout=60)  # we set the duration of the poll to 1 minute

        # Next we will create some pages using the `add_page` method. This is done the same way you would create an Embed
        # idiomatically using `discord.Embed()`, but it also takes an on_next and buttons arguments. Buttons should be a
        # list of valid Discord emojis -- these can be Emoji objects or Unicode strings. In this case, we defined the
        # emojis as unicode strings directly within the list. It may make sense to define them ahead of time so you can
        # reuse them later, though.
        #
        # `on_next` must be a reference to a function. Remember, when you pass a reference to the function you should NOT
        # use () parenthesis at the end of the function name. That would call the function immediately, as pages were being
        # created. Instead, the reference will be called by the menu loop at a later time.
        first = await menu.add_page(title='Sun vs Moon Poll', description='Do you prefer the sun or the moon?',
                                    on_next=self.finish, buttons=['\U00002600', '\U0001F315'])
        first.set_footer(text="Only vote once! Your vote won't count if you cheat!")

        # Note that we didn't include an `on_next` or any `buttons` on the last `Page`. This is important as it denotes
        # this will be our final and closing page on the menu. What this means is that when you arrive at this page,
        # no matter how it was done, the menu loop will be closed and no longer respond to user input.
        await menu.add_page(title='Sun vs Moon Poll', description=f'Results are in!')

        # Finally, after all our menu pages are constructed, we can use the `open()` method on our menu object to
        # start the menu loop.
        await menu.open()

    # Here we are defining the functions our pages reference (this is your `on_next` parameter). These should always take
    # a menu object (in this case ButtonMenu) so we can test against the input!
    @staticmethod
    async def finish(m: Poll):
        # `generate_results_page` is a special utility method on a `Poll` that will construct embed fields, perform math to
        # calculate the winner, and append it to your 'final' page. If you want custom fields or to build your embed
        # uniquely, you would want to skip using this method and build your embed object here on your own.
        await m.generate_results_page()

        # `next()` is a built-in method on the menu object that does what it sounds like -- moves to the next page.
        await m.next()


def setup(client: commands.Bot):
    client.add_cog(MyPoll(client))
