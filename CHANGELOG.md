# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.1.5] - 2021-2-06

Fixes a security issue in the `urllib` dependency for versions prior to 1.26.5.

## [2.1.4] - 2021-19-05

### Changed

- Optimized how menus handle reaction events in different channel types.

## [2.1.3] - 2021-15-05

### Changed

- Fixed a regression where buttons weren't being handled safely in DM's.
- Fixed an uncommon occurrence where closing menus would raise an AttributeError instead of returning.

## [2.1.2] - 2021-14-05

### Changed

- Fixed a bug where PaginatedMenus did not check for an existing cancel page when closing *(`.set_cancel_page()`)*.

## [2.1.1] - 2021-13-05

### Changed

- Fixed a bug where closing out certain menus would result in trying to remove reactions on None-types (see #54).
- Fixed a bug with input logic flow on button menus that would result in raising InvalidArgument errors.
- Fixed a bug where session force closing would raise an InvalidArgument error.

## [2.1.0] - 2021-13-05

### Added

- Session settings for users can now be set. Please note the system isn't complete yet, but you can now keep 
  multiple menus alive at the same time, or have the earliest one close if  there are too many. Currently, only the 
  user limit applies. Please see [the book](https://dpymenus.com/sessions.html) for more information.

### Changed

- Updated several book instructions in regard to installing and running examples on Windows.
- Removed an old dev dependency carry-over from the example runner *(uvloop)* that caused issues on Windows.

## [2.0.0] - 2021-13-05

### Highlight Features

- **Templates**: you can now apply styles across entire menus by using the new
  **[templating system](https://dpymenus.com/templates.html)**
- **Hooks**: various menu events can now be **[hooked](https://dpymenus.com/hooks.html)** into with your own functions
- **Settings**: almost all settings are now configurable via a
  **[configuration file](https://dpymenus.com/global_configuration.html)**
- **Documentation**: the **[API docs](https://dpymenus.readthedocs.io/en/latest/)** have been reworked, a
  **[book](https://dpymenus.com/)** has been added with lots of detailed information, and
  several **[new examples](https://github.com/robertwayne/dpymenus/tree/master/examples)** were added
  *(additionally, all old examples were updated)*.

### Added

- Session handling has been completely rewritten. This technically will not be fully functional until v2.1, but from an
  external view, it will work the exact same *(without some of the common annoyances from before)*.
- The new Discord `reply` feature is now supported by menus. This can be configured via settings.
- Menus now support setting an initial page with a new method: `.set_initial_page()`.
- Examples can now be run with a built-in bot.

### Changed

- Buttons are now throttled by default to avoid filling up rate limit buckets too quickly. This was a source of much
  confusion. This can be configured via settings.
- Destination errors now fail gracefully.
- Fixed many bugs and optimized various logic paths.

### Removed

- `.allow_multisession()` no longer exists. This is the default now *(as per popular request)*, and can be configured
  via settings.
- Support for Python 3.7

### Internal

- Poetry is now the package and build tool.
- Black is now the formatter.
- Almost all the internal code was rewritten resulting in better performance and/or cleaner code. Note that this could
  mean your menus will break, if you were using any internally marked methods *(prefixed with an underscore)*.

## [1.3.1] - 2021-01-22

### Changed

- Fixed a bug where ButtonMenu did not have the timeout set. (#33)
- Fixed a bug with Poll callback validation.
- Refactored PaginatedMenus to now use the same timeout & close handling that all menu types do.

## [1.3.0] - 2021-01-09

### Changed

- Menus now only require a single page to successfully build. *The original reasoning behind having this restriction was
  based on the fact that a menu is generally going to consist of many pages. However, there have bene several use-cases
  such as reloadable pages and dynamically generated menus, that may result in just a single page.*
- Fixed `reloadable_data_example.py` having a missing import.
- Updated `reloadable_data_example.py` to reflect the page validation change and remove the workaround requiring an
  empty blank page.
- Updated dependency on `discord.py` to `1.6`.

## [1.2.3] - 2020-12-10

### Added

- New example showing how to reload data without executing a page transition.

### Changed

- Fixed a bug where PaginatedMenu & ButtonMenu types were not having their output set correctly when
  using `set_destination`. This would raise a NotFound error in DM channels. (#27)
- Fixed a bug where the reaction check predicates were incorrectly assuming Member-type instead of User-type. This would
  cause raw reaction events to not be read in DM channels. (#27)
- ButtonMenu types now clean up their output on page transition in DMs.

## [1.2.2] - 2020-10-08

### Added

- Menus now expose a history attribute, an ordered list of user-visited pages. This lasts until the menu is closed.
- Added new helper method `.last_visited_page()` -- returns the last page index that a user had visited.

### Changed

- ButtonMenu buttons will no longer refresh if the pages' index has not changed. This helps curb rate limiting, as well
  as provides a cleaner end-user experience.
- Updated the API docs to include Page properties and methods.
- Refactored internal `next` events to remove repeated code.
- Removed redundant internal checks.

## [1.2.1] - 2020-10-07

### Changed

- Fixed a bug where button indexes would become offset based on method call order.
- Fixed a bug where page numbers would not be shown based on method call order.
- Fixed a typo in the poll_example.py file so it now works correctly again.
- Clarified when the `next` event was emit in the README.

## [1.2.0] - 2020-09-29

### Changed

- Dropped support for discord.py versions < 1.5 due to mandatory breaking changes with the Discord API and the new
  Intents system. This is a forced change as of October 7th. You can read more
  [here](https://discordpy.readthedocs.io/en/latest/intents.html#intents-primer).

## [1.1.0] - 2020-09-16

### Changed

- Fixed a bug where bot reactions were being captured by the menu event loop when using the raw reaction event API.
- All raised errors are now caught and logged appropriately.
- Fixed a bug where certain custom Emoji objects would fail as buttons.
- PaginatedMenu & ButtonMenu now refresh their output attr after buttons have been added. This allows them to be
  referenced with the `.reactions` value.
- Optimized PaginatedMenu when using default buttons by skipping intensive check paths.
- Optimized PaginatedMenu reaction_add/remove event checks when using default buttons by skipping intensive check
  predicate.
- Internal type var `PageEmbed` renamed to `PageType`; added `Dict` type to the new type var.
- Fixed a bug where the bot was counting its own reactions when tallying poll votes.
- Fixed a bug where specific mixes of emoji types would crash a ButtonMenu.
- Fixed a bug where a user applying a non-button reaction to a menu in a ButtonMenu would cause it to reload the page,
  forcing all the buttons to be added again.
- Moved the private _is_cancelled method into TextMenus, as it is only called in that class.
- Examples have been updated to showcase any new features.

### Added

- Logger added to the library as 'dpymenus'.
- `emoji` added as a dependency for fast, safe unicode emoji lookups, button checks, and conversions.
- PaginatedMenu now does pre-validation on provided buttons.
- The `.add_pages()` method can now take a dictionary-style embeds *(though I do recommend against this unless you're
  retrieving JSON data)*.
- Added a new helper method for ButtonMenu styles: `button_pressed` -- this is meant for simplifying the check for which
  button was pressed in your `on_next` callbacks. It takes the button you are checking for and returns True when the
  button you passed in is the same as what the menus received input was.
- Added a new helper method for TextMenu
  styles: `response_is' -- this is meant for simplifying the check for what a user had typed in when building your `
  on_next` callbacks. It takes a string or a list of strings and returns True when the text passed in matches what the
  user had typed.
- Added a new menu option for TextMenus: `normalize_responses` -- if called on your menu instance, user text responses
  will be stripped of whitespace *(incl. leading, trailing, and anything over 2 spaces within)* and lower-cased.
- Internally, added a new TypeVar: `Button` to replace `Union[Emoji, PartialEmoji, str]`.

### Removed

- The default cancel page has been removed from all menu styles to align with PaginatedMenus behavior. As these menu
  styles define an `on_cancel` callback, users can still add their own in if they wish. This is primarily for
  consistency across the library.

## [1.0.0 - 1.0.4] - 2020-09-12

This marks the first stable release of dpymenus. As of now, I will not be making any breaking changes to the API without
a major version increase. This release also sees the finalization of the fluent-interface style for building menus, as
well as various bug fixes, stability fixes, stronger error handling and validation, and better customizability for
users.

### Changed

- **Breaking:** Menus options are now set via fluent-interface style of programming rather than parameters. The primary
  influences for this change was a growing number of options (which meant very long parameter lists) and the benefit of
  matching how discord.py builds Embed objects -- this means it is more familiar to users of the library, even if they
  aren't completely familiar with that paradigm.
- Sessions are now stored as a dictionary with the keys being a tuple of (user_id, channel_id) now. This is faster for
  lookups, and allows the menu reference to be carried outside the current menu, so session limiting is more flexible.
  This was primarily changed to allow the new `allow_multisession` option.
- The BaseMenu class now subclasses ABC.
- **Breaking:** The `.cancel()` method on menus is now `.close()`. The reason for this change is convention -- it aligns
  with `.open()` better.
- Reactions now use the raw_reaction event API.
- Menus now utilize properties to define their option attributes.
- **Breaking:** Pages now use \_\_slots\_\_ to define their attributes for increases performance / memory usage.
- All examples updated to use the latest features.
- Fixed a bug where `add_pages` would not handle mixed Page and Embed objects gracefully.

### Added

- Pages now have an `index` attribute instead of the menu class storing only the current index.
- Improved validation checks for menu errors. Stronger error handling will be a focus of v1.1, however.
- Many new methods for use with menu objects to define their options. See the README section titled 'Menu Options' or
  the API documentation for a complete list.

### Removed

- **Breaking:** Removed the `.add_page()` method in favor of `.add_pages()` and the new fluent-style. It reduces bot
  code, reduces visual noise, and makes it easier to reason about where things happen in your menu with dense or complex
  embeds.
- **Breaking:** Removed the `page_index` attribute from `BaseMenu` in favor of each `Page` storing its own index in the
  order it was processed in from the `.add_pages()` method. As this takes a list, the order will be safely carried over.
  This also allows the user to swap pages simply by changing their order in the menu, and change the menu page order at
  runtime.
- **Breaking:** Pages no longer have an `embed` parameter, as they subclass Embed and use internal methods to handle
  safe handling and display.
- **Breaking:** All menu and page optional parameters have been removed in favor of methods.
- Inline comment guides in examples have been removed in favor of a small tutorial website that is being worked on.

## [0.3.5] - 2020-08-12

### Added

- Menus now accept a `destination` parameter, which takes a User or Channel object. This will open the menu in that
  channel as opposed to in the current channel.

### Changed

- **Breaking:** Broke the `next` method out into two methods: `next` and `go_to`. `next` no longer takes any
  parameters (previously took `name`) to jump to a different page. `go_to` acts the same as the old `next` code, but
  takes a `name_or_index` parameter to accurately reflect the change in *0.2.8* where you could jump to indexes as well.
  The reason behind this was to simplify the branching code and user readability.
- The default cancelled embed now has the title *'Cancelled'* instead of the last pages title.
- Refactored a lot of older code, particularly the subclasses of BaseMenu.
- Rewrote the README; removed the old usage sections for a simplified *'Getting Started'* section. Added in information
  about new features, such as `destinations`.
- Updated to the latest discord.py version: 1.4.1
- Simplified some examples by removing 'fluff' code.

## [0.3.4] - 2020-07-25

### Fixed

- Fixed an issue where string-type emoji would not pass a `ButtonMenu`
  check.

## [0.3.3] - 2020-07-23

*dpymenus works with Python 3.9 beta.*

### Changed

- Moved various checks into standing methods instead of lambdas for caching opportunities.
- Refactored some repeated code paths.

### Fixed

- Fixed an issue where adding a custom reaction to a `ButtonMenu` or
  `PaginatedMenu` would raise an HTTP 400 and lock the menu.
- Fixed various typos and grammatical errors within the documentation.

## [0.3.2] - 2020-07-22

### Added

- `PaginatedMenu`s can now pass in an `Embed` to `on_cancel` and `on_timeout`
  to override the default embeds.
- Created a little logo.

### Changed

- Replaced old demos with a new demo .gif for the README showing off a `PaginatedMenu`.
- Modified build script to avoid the possibility of uploading old source code to PyPi.
- Updated all `__repr__` strings to more accurately capture the object representation.
- `start_session` is now marked private with `_`.
- Moved license in setup to display properly with `pip show dpymenus`.
- Updated `discord.py` requirement to `1.3.4`.

## [0.3.1] - 2020-07-18

### Added

- `PaginatedMenu`s now have an optional argument: `page_numbers`. If set to `True`, embeds will generate a footer with
  the current and total page numbers. *This option will override user-defined footers.*

### Changed

- The session handler now stores sessions as a tuple `(user_id, channel_id)`
  instead of just `user_id`.
- The default timeout page now has the title 'Timed Out' instead of the last pages' name.
- **Breaking:** `set_user_inactive()` is now `close_session()`

### Fixed

- Users can now have multiple menu sessions cross-channel and guild.
- Fixed a timeout error in a `TextMenu` where it did not break after the exception occurred.
- Fixed a timeout error in all menus where it attempted to remove null data from the session list.
- Fixed an issue where other menu buttons would call your own menu actions.
- Added a missing `await` in the README example for `PaginatedMenu`.

## [0.3.0] - 2020-07-17

### Added

- A new menu type, PaginatedMenu. See examples on how to use this feature. *`PaginatedMenu`s are very basic currently.*

- Users can now only create a single menu instance at a time in order to prevent abuse or confusion. *Note that if you
  are overriding `on_cancel` or
  `on_timeout`, you need to call `set_user_inactive()` alongside
  `self.active = False` now.*

### Fixed

- `ButtonMenu`s no longer send new messages inside DM channel types instead of the expected default behaviour.
