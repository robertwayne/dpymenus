<h1 align="center">Discord Menus</h1>
    
<div align="center">
  <strong><i>Simplified menus for discord.py developers.</i></strong>
  <br>
  <br>
  
  <a href="https://pypi.org/project/dpymenus/">
    <img src="https://img.shields.io/pypi/v/dpymenus?color=0073B7&label=Latest&style=for-the-badge" alt="Version" />
  </a>

  <a href="https://dpymenus.readthedocs.io/en/latest/">
    <img src="https://img.shields.io/readthedocs/dpymenus/latest?style=for-the-badge" alt="Docs" />
  </a>
  
  <a href="https://python.org">
    <img src="https://img.shields.io/pypi/pyversions/dpymenus?color=0073B7&style=for-the-badge" alt="Python Version" />
  </a>
</div>

<br>

-----

<img align="right" src="assets/demo.gif" alt="user creates an embed, reaction buttons are added, and user navigates the menu
by clicking the buttons">

### Table of Contents
**[Documentation](https://dpymenus.readthedocs.io/en/latest/?badge=latest)**
+ [Getting Started](#getting-started)
+ [Menu Options](#menu-options)
+ [Helper Methods](#helper-methods)
+ [Building Pages](#building-pages)
+ [Event Callbacks](#event-callbacks)
+ [Generic Input Matching](#generic-input-matching)
+ [Reaction Buttons](#reaction-buttons)
+ [Poll Utilities](#poll-utilities)
+ [Logging](#logging)

<br>
<br>

-----

### Getting Started
`dpymenus` is an unofficial add-on for the `discord.py` library that lets you quickly compose various styles of 
menus *(text, buttons, polls)* which react to user input.

You can install the library with `pip install dpymenus`.

This very basic example will get a menu running similar to the one in the .gif!

```python
from discord.ext import commands
from dpymenus import Page, PaginatedMenu


class Demo(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def demo(self, ctx: commands.Context):
        page1 = Page(title='Page 1', description='First page test!')
        page1.add_field(name='Example A', value='Example B')

        page2 = Page(title='Page 2', description='Second page test!')
        page2.add_field(name='Example C', value='Example D')

        page3 = Page(title='Page 3', description='Third page test!')
        page3.add_field(name='Example E', value='Example F')

        menu = PaginatedMenu(ctx)
        menu.add_pages([page1, page2, page3])
        await menu.open()


def setup(client):
    client.add_cog(Demo(client))
```

There are more examples in the *examples* directory above for each menu style *(Text, Button, Paginated, and Polls)*.

Can't find something you were looking for? Open an issue and I'll add a relevant example!

### Menu Options
Menus use fluent-style chaining, similar to how one builds a discord.py Embed, to set their behaviours. Below is a list
of methods available for chaining, and what they do. If you are unfamiliar with how to use these, look at the examples in
the *examples/* directory for various ways to compose and apply these options.

#### All Menu Types
`.add_pages(x)` -- takes a list of Embed or Page objects and turns them into menu pages.

`.set_timeout(x)` -- takes an integer and sets the duration *(in seconds)* before the menu will timeout.

`.set_destination(x)` -- takes a User, TextChannel, or Context object and sends all menu output to that location.

`.show_command_message()` -- prevents the message that invoked the menu from being deleted when the menu opens.

`.persist_on_close()` -- prevents the menu from being deleted when closed. Clears reactions and remains on the last page.

#### Text & Button Menus
`.set_data(x)` -- takes a dictionary of arbitrary data that can be used across menu and page functions.

#### Text Menus
`.set_delay(x)` -- takes an integer and sets the duration *(in seconds)* before the users response message will be deleted.

`.normalize_responses()` -- user text responses will be stripped of whitespace *(incl. leading, trailing, and anything over 2 spaces within)* and lower-cased

#### Paginated Menus
`.buttons(x)` -- takes a list of Emoji or str objects and uses them to replace the default buttons. Must be 3 or 5 in length.

`.set_cancel_page(x)` -- takes an Embed or Page object and displays that page when a user cancels the menu.

`.set_timeout_page(x)` -- takes an Embed or Page object and displays that page when the menu times out.

`.show_page_numbers()` -- adds pages numbers to the footer of each menu page *(in current_page/total_pages format)*. Overwrites
user set footers.

`.show_skip_buttons()` -- adds two extra buttons to the menu, one for skipping to the first page and one for the last page.

`.hide_cancel_button()` -- removes the cancel button from the menu.

`.allow_multisession()` -- disables the one menu per user+channel session limit. Old menus are closed when a new one is opened.

### Helper Methods
`.next()`, `.previous()` -- goes forward or backward one page.

`.to_first()`, `.to_last()` -- jumps to the first or last page.

`.go_to(x)` -- takes a string or integer *(on_next function name or page index)* and jumps to that specific page. 
Useful for non-linear menus.

`.button_pressed(x)` -- takes an Emoji or str button and returns True if that was the button the user had pressed.
Only usable on ButtonMenu.

`.response_is(x)` -- takes a string or list of strings and returns True if that matches what a user had typed.
Only usable on TextMenu.


### Building Pages
Menus are built with Embed objects, but the library also defines a subclass of Embed which is Page. Menus can 
take a mix of Embed and Page objects when you call the `add_pages()` method, and although there are use cases, 
I recommend defining all pages as Page objects to keep your codebase clear and understandable. Pages have additional 
methods and attributes available:

`.buttons(x)` -- takes a list of Emoji or str objects to display on the page.

`.index()` -- returns the page index in the menu.

Additionally, pages have methods for defining callbacks based on specific events. See the next section for information
on events, how to call them, and what menus they each work on.

### Event Callbacks
By default, the base menu implements methods for all events except `next`, which should
be handled by the user. Events can be overridden using `.on_EVENTNAME` methods when creating your
menu object. Note that Polls and Paginated menus implement their own `next` event methods
and should not be overwritten.

**Events**

- **next** -- Emit when the menu instance calls `.next()`. 

- **fail** -- Emit when user input on a page is invalid. Usable on Text menus.

- **timeout** -- Emit when a menu times out. Usable on Text, Button, and Paginated menus.

- **cancel** -- Emit when a menu is cancelled from user input. Usable on Text, Button, and Paginated menus.

*You can see these in use in the text, button, and poll menu examples.*


### Generic Input Matching
For Text Menu styles, the library contains some preset constants for quick, generic use-cases. You can
import what you need by name, or all at once like such:

`from dpymenus.constants import *`

The defaults are:
```python
CONFIRM = ('y', 'yes', 'ok', 'k', 'kk', 'ready', 'rdy', 'r', 'confirm', 'okay')
DENY = ('n', 'no', 'deny', 'negative', 'back', 'return')
QUIT = ('e', 'exit', 'q', 'quit', 'stop', 'x', 'cancel', 'c')
```

### Reaction Buttons
Here are some examples of how to acquire emojis in discord.py for custom buttons:

```python
btn1 = client.get_emoji(3487239849812123)  # guild emoji
btn2 = discord.utils.get(ctx.guild.emojis, name='example')  # guild emoji
btn3 = '<:example2:35434643573451>'  # guild emoji
btn4 = '\N{SNAKE}'  # unicode emoji as text
btn5 = '\U00002714'  # unicode emoji codepoint :heavy_check_mark:
```

### Poll Utilities
Polls have a handful of quick utility methods built-in that should make using them simpler and faster for most
use case scenarios.

`.results()` -- Returns a dictionary where the keys are the poll choices, and the values are the final vote tally.

`.add_results_fields()` -- Adds all the result fields to your closing page.

`.generate_results_page()` -- Adds all the result fields to your closing page as well as calculates the winner or 
a draw.

### Logging
If you just wish to have basic logging, you can enable it by placing this at the start of your code:

```python
import logging

logging.basicConfig(level=logging.INFO)
```

If you are looking to customize the logger, you can use the example below for an idea on how to set it up.

```python
import logging
import sys

menus_logger = logging.getLogger('dpymenus')
menus_logger.setLevel(logging.INFO)
menus_handler = logging.StreamHandler(sys.stdout)
menus_handler.setFormatter(logging.Formatter('[%(name)s] %(message)s'))
menus_logger.addHandler(menus_handler)
```

-----

Check out my other discord.py utility: **[cogwatch](https://github.com/robertwayne/cogwatch)** -- *Automatic hot-reloading for your discord.py command files.*
