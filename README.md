[![PyPI version](https://badge.fury.io/py/dpymenus.svg)](https://badge.fury.io/py/dpymenus)

# Discord Menus

`dpymenus` is an add-on for the `discord.py` library that lets you quickly build stateful
menus that respond to chat input within the Discord client.

+ [Installation](#installation)
+ [Usage](#usage)
+ [State Fields](#state-fields)
+ [Generic Input Matching](#generic-input-matching)
+ [Reaction Buttons](#reaction-buttons)
+ [Examples](#examples)

### Installation
`pip install dpymenus`

### Usage
First, you must build a list of Page objects. Pages extend discord.py
Embed objects, so you construct it the exact same way, but you add a `func` paramater.

As an example:

    new_page1 = Page(title='First Page', description='This is a test.', func=<FUNCTION_REFERENCE>)
    new_page2 = Page(title='Second Page', description='This is also a test.')

The `func` should point to a function which will be called when the page is opened. This is
where you do validation and handle user input.
    
Then you can create your menu object *(it must take the command Context as its first param)*:

    menu = Menu(ctx, pages=[new_page, new_page2])
    
Lastly, call the `run()` method on it:

    await menu.run()
    
...and you're *(mostly)* finished! A menu loop will spawn and handle user input when the command is 
called until it times out or is cancelled by the user.

Your function references inside the pages should include a 'final' page where the
function is `None`. When the final page in your pages list is displayed, the menu will call a
close method and end the loop.

Your function reference should call the `menu.next()` method whenever it has
successfully handled input. `next()` also takes 1 optional argument: 

`name`: jumps to a specific page by its function reference name. Useful for non-linear menus.

You denote a final page, or 'ending' to the menu, by not supplying an empty `func` parameter *(or passing `None`)*.
    
### State Fields
In addition to standard menu setup, optional `state_fields` can be defined for variables or objects you
want to pass around in page functions.

State fields should be defined in a dictionary:

    state_fields = {'username': None, 'favorite_color': None}

...and then passed into your menu on initialization:

    menu = Menu(ctx, pages, state_fields)

You can then access these like any objects attributes *(ie. `x = menu.state_fields['value']`)*.

*As it is simply a dictionary, you can set more than simple input strings. For instance,
transferring objects across functions by setting the value to an object. Ideally, the menu 
object should contain all your state until it is ready to be processed. This also simplifies
your code by limiting the amount of parameters functions need to accept when handling
multiple objects related to a single menu.*

### Generic Input Matching
The Menu class contains several generic values ready for matching against user input. These values
are generally universal, but should you wish to override them with your own values, there is a 
class method called `override_generic_values(value_type, replacement)` that can be called anywhere
in your code to replace them completely.

`value_type` is one of three strings: `'confirm'`, `'deny'`, or `'quit'`.

`replacement` is a tuple of strings containing your new values.

The defaults are:
```python
generic_confirm = ('y', 'yes', 'ok', 'k', 'kk', 'ready', 'rdy', 'r', 'confirm', 'okay')
generic_deny = ('n', 'no', 'deny', 'negative', 'back', 'return')
generic_quit = ('e', 'exit', 'q', 'quit', 'stop', 'x', 'cancel', 'c')
```

### Reaction Buttons
If you are interested in using emoji-based reaction buttons on your
menu instead of text, they are easy to plug in. Each Page object can
be passed a list of emojis with the `buttons` parameter.

Here are some examples of how to acquire emojis in discord.py:
```python
btn1 = client.get_emoji(3487239849812123)  # guild emoji
btn2 = discord.utils.get(ctx.guild.emojis, name='example')  # guild emoji
btn3 = '<:example2:35434643573451>'  # guild emoji
btn4 = '\N{SNAKE}'  # unicode emoji as text
btn5 = '\U00002714'  # unicode emoji codepoint :heavy_check_mark:
```

### Examples
A simple, linear cog that demonstrates a text-based menu.
```python
from discord.ext import commands
from discord.colour import Colour

from dpymenus.menu import Menu
from dpymenus.page import Page


class Ping(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        confirm_page = Page(title=f'Ping Menu', color=Colour.red(), func=self.confirm,
                            description=f'Are you absolutely sure you want to send a ping command?\n\n'
                                          'Type `yes` if you are sure.\nType `quit` to cancel this menu.')

        complete_page = Page(title='Ping Menu', color=Colour.green(),
                            description='Pong!')

        menu = Menu(ctx, pages=[confirm_page, complete_page])
        await menu.run()

    @staticmethod
    async def confirm(m: Menu) -> None:
        if m.input.content in m.generic_confirm:
            await m.next()


def setup(client: commands.Bot):
    client.add_cog(Ping(client))
```
A simple, non-linear cog that demonstrates a reactive button-based menu.
```python
import discord.utils
from discord.colour import Colour
from discord.ext import commands

from dpymenus.menu import Menu
from dpymenus.page import Page


class ButtonsCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

@commands.command()
async def buttons(self, ctx: commands.Context) -> None:
    # if you copy this example, you will need to change these custom guild emoji lines
    btn1 = self.client.get_emoji(552018703357837312)  # guild emoji :mana:
    btn2 = discord.utils.get(ctx.guild.emojis, name='health')  # guild emoji
    btn3 = '<:low_gold:548414699243307028>'  # guild emoji
    btn4 = '\N{SNAKE}'  # unicode emoji as text
    btn5 = '\U00002714'  # unicode emoji codepoint :heavy_check_mark:

    confirm_page = Page(title=f'Ping Menu', color=Colour.red(), func=self.confirm, buttons=[btn1, btn2],
                        description=f'The mana emoji moves on, the health emoji cancels the menu.')

    second_confirm_page = Page(title='So many buttons!', color=Colour.orange(), func=self.confirm_again, buttons=[btn3, btn4, btn5])

    complete_page = Page(title='Ping Menu', color=Colour.green(), description='Pong!')

    menu = Menu(ctx, pages=[confirm_page, second_confirm_page, complete_page])
    await menu.run()

@staticmethod
async def confirm(m: Menu) -> None:
    if m.input == 'mana':
        await m.next()

    elif m.input == 'health':
        await m.cancel()

@staticmethod
async def confirm_again(m: Menu) -> None:
    if m.input == 'low_gold':
        await m.next()

    elif m.input == '\N{SNAKE}':
        await m.next('confirm')  # this will take us back to the previous page

    elif m.input == '\U00002714':
        await m.cancel()


def setup(client: commands.Bot):
    client.add_cog(ButtonsCog(client))
```
