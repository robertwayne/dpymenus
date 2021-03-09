# <h1 align='center'>Discord Menus</h1>

<div align='center'>
  <strong><i>Simplified menus for discord.py developers.</i></strong>
  <br>
  <br>

  <a href='https://pypi.org/project/dpymenus/'>
    <img src='https://img.shields.io/pypi/v/dpymenus?color=0073B7&label=Latest&style=for-the-badge' alt='Version' />
  </a>

  <a href='https://dpymenus.readthedocs.io/en/latest/'>
    <img src='https://img.shields.io/readthedocs/dpymenus/latest?style=for-the-badge' alt='Docs' />
  </a>

  <a href='https://python.org'>
    <img src='https://img.shields.io/pypi/pyversions/dpymenus?color=0073B7&style=for-the-badge' alt='Python Version' />
  </a>
</div>

<br>

---

This directory contains runnable examples of various menus. If you wish to run the test bot, you will need to supply a
personal bot token -- otherwise it will not run.

### Run the test bot:

`poetry run examples`

### Examples

| File      | Command | Description |
| ----------- | ----------- | ----------- |
| button_menu_example.py      | .buttons | Shows a menu that has different buttons on each page.       |
| paginated_menu_example.py   | .paginated | Shows a menu that has static buttons to move through pages.        |
| paginated_menu_list_example.py | .paginated2 | Shows a menu that chunks a list of variably sized data and shows 10 items per page. |
| template_example.py | .templates | Shows a menu utilizing the templating feature in v2. |
| poll_example.py | .poll | Shows a menu that counts votes for choices and tallies them up. |
| reloadable_data_example.py | .reloadable | Shows a menu with a single page that has dynamic data updated on button presses. |
| text_menu_example.py | .text | Shows a menu that reacts based on user text responses. |
