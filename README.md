[![PyPI version](https://badge.fury.io/py/dpymenus.svg)](https://badge.fury.io/py/dpymenus)

# Discord Menus
`dpymenus` is an add-on for the `discord.py` library that lets your quickly build stateful
menus that respond to chat input within the Discord client.

### Installation
`pip install dpymenus`

### Usage
First, you must instantiate a new Menu. You must pass in a reference to your bot client and 
the message context. In addition, you must build a list of Page objects.

Page creation is simple:

    new_page = Page('page_1', embed, func)
    new_page2 = Page('page_2', embed2, func2)

The page name is a string and can be anything you want. The embed should point to a Discord
Embed object. The func should point to a function or method which will handle validation and
other features you want your menu to accomodate.

In addition, optional 'capture fields' can be named for more advanced menus that need to store
many user input variables *(eg. storing a user name and favorite color for storage in a DB later)*.

Capture fields can be declared with a dictionary:

    captures = {'username': None, 'favorite_color': None}
    
Finally, you can create our menu object:

    menu = Menu(self.client, ctx, pages=[new_page, new_page2], capture_fields=captures)
    
Once that is done, you simply call the `run()` method on our new Menu object:

    await menu.run()
    
...and you're *(mostly)* finished! A menu loop will spawn and handle user input when the command is 
called until it times out or is cancelled by the user.

Your function or method references inside the pages should include a 'final' page where the
function is `None`. When the final page in your pages list is displayed, the menu will call a
close method and end the loop.

Your function or method reference should call the `menu.next_page()` method whenever it has
successfully handled input. `next_page()` also takes 2 optional arguments: 

`specific_page`: jumps to a specific page by name. Useful for edit options or non-linear menus.

`quiet_output`: prevents the page from displaying its embed when called.
    
### Example
This is an example of a simple cog that confirms if you want to send the 'ping' or not.
```python
import discord
from discord.ext import commands
from discord.colour import Colour

from dpymenus.menu import Menu
from dpymenus.page import Page

class Ping(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        confirm_embed = discord.Embed(title=f'Ping Menu',
                                      description=f'Are you absolutely sure you want to send a ping command?\n\n'
                                                  'Type `yes` if you are sure.\nType `quit` to cancel this menu.',
                                      color=Colour.red())

        complete_embed = discord.Embed(title='Ping Menu', 
                                       description='Pong!', 
                                       color=Colour.green())

        menu = Menu(self.client, ctx, pages=[Page('confirm', confirm_embed, self.confirm), 
                                             Page('complete', complete_embed, None)])
        await menu.run()

    @staticmethod
    async def confirm(m: Menu) -> None:
        if m.input_message.content in ('y', 'yes'):
            await m.next_page()

def setup(client: commands.Bot):
    client.add_cog(Ping(client))
```

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


### Todo
- Allow user to replace the Discord Colour class with their own class or file.
- Clean up and rewrite doc strings.
- Flesh out Exception handling.
- Add examples for complex / non-linear menus.
