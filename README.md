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

<img align="right" src="assets/demo.gif" alt="user creates an embed, reaction buttons are added, and user navigates the
menu by clicking the buttons">

### Table of Contents

**[Book](https://dpymenus.com)** <br>
**[API Docs](https://dpymenus.readthedocs.io/en/latest/?badge=latest)** <br>
**[Examples](https://github.com/robertwayne/dpymenus/tree/master/examples)**

- [Features](#Features)
- [Using](#Using)
- [Example](#Example)
- [Support](#support)
- [Contributing](#contributing)

<br>
<br>

---
<div align="center">
  <h1>
    You are viewing the active dev branch.
    There are no stability or documentation guarantees on this branch.
  </h1>
</div>

### Features

`dpymenus` is an unofficial add-on for the `discord.py` library that lets you quickly compose various styles of menus
which react to user input.

- Handles text & button input, normalization, and validation
- Easy-to-build menus with paginated data, multiple choices, and polls
- Template system for quickly defining a cohesive style for your menus
- User-defined callbacks & event hooks for complex use-cases
- Awesome examples and documentation to get rolling quickly

### Using

`dpymenus` has a lot of functionality, so I strongly recommend browsing through **[the book](https://dpymenus.com)**
for any questions you might have. In addition, the
**[examples directory](https://github.com/robertwayne/dpymenus/examples)** contains tons of working examples for almost
every feature of the library.

### Example

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

### Support

If you are looking for support on how to use particular library functions, please ask in the
**[discussions](https://github.com/robertwayne/dpymenus/discussions)** tab. If you've encountered a bug,
**[submit an issue](https://github.com/robertwayne/dpymenus/issues/new)**.

In addition, feel free to add me on Discord @ `Rob (롭)#0013` -- I am open to discuss the library and assist when I am
free, but I prefer you use the GitHub options as it may help other people as well.

### Contributing

`dpymenus` is open-source for a reason -- I welcome all additions, bug fixes, and changes if they fit within the scope
of the library. Please see the **[contributing chapter](https://dpymenus.com/contributing.html)**
in the book for detailed information. Don't be shy!
