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

---

<img align="right" src="assets/demo.gif" alt="user creates an embed, reaction buttons are added, and user navigates the menu
by clicking the buttons">

### Table of Contents

**[Documentation](https://dpymenus.readthedocs.io/en/latest/?badge=latest)** <br>
**[Examples](https://github.com/robertwayne/dpymenus/tree/master/examples)**

- [Getting Started](#getting-started)
- [Menus](#menus)
- [Pages](#pages)
- [Templates](#templates)
- [Hooks](#hooks)
- [Configuration](#configuration)
- [Sessions](#sessions)
- [Logging](#logging)
- [Cogwatch Integration](#cogwatch-integration)
- [Tips](#tips)
- [Support](#support)
- [Contribute](#contribute)
- [FAQ](#faq)
- [Migration v1 -> v2](#migration)

<br>
<br>

---

### Features
`dpymenus` is an unofficial add-on for the `discord.py` library that lets you quickly compose various styles of
menus which react to user input.

- Handles text & button inputs
- Easy-to-build menus with paginated data, multiple choices, and polls
- Template system for quickly defining a cohesive style for your menus
- User-defined callbacks & event hooks for complex use-cases
- Awesome examples and documentation to get rolling quickly

### Getting Started
Install the library with `pip install dpymenus` or `poetry add dpymenus`.

This very basic example will get you a menu like the one in the .gif!

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

The __examples__ directory contains many fully-functional cogs showing off all the menu types, various integrations,
and advanced features available in the library!


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

---

Check out my other discord.py utility: **[cogwatch](https://github.com/robertwayne/cogwatch)** -- _Automatic hot-reloading for your discord.py command files._
