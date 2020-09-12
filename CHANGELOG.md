
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.0.0 - 1.0.4] - 2020-09-12
This marks the first stable release of dpymenus. As of now, I will not be making any breaking changes to the API without
a major version increase. This release also sees the finalization of the fluent-interface style for building menus, as
well as various bug fixes, stability fixes, stronger error handling and validation, and better customizability for users.

### Changed
- **Breaking:** Menus options are now set via fluent-interface style of programming rather than parameters. The primary 
influences for this change was a growing number of options (which meant very long parameter lists) and the benefit of
matching how discord.py builds Embed objects -- this means it is more familiar to users of the library, even if they 
aren't completely familiar with that paradigm.
- Sessions are now stored as a dictionary with the keys being a tuple of (user_id, channel_id) now. This is faster for
lookups, and allows the menu reference to be carried outside the current menu, so session limiting is more flexible. This
was primarily changed to allow the new `allow_multisession` option.
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
- Many new methods for use with menu objects to define their options. See the README section titled 'Menu Options'
or the API documentation for a complete list.

### Removed
- **Breaking:** Removed the `.add_page()` method in favor of `.add_pages()` and the new fluent-style. It reduces
bot code, reduces visual noise, and makes it easier to reason about where things happen in your menu with dense or
complex embeds.
- **Breaking:** Removed the `page_index` attribute from `BaseMenu` in favor of each `Page` storing its own index in the
order it was processed in from the `.add_pages()` method. As this takes a list, the order will be safely carried over.
This also allows the user to swap pages simply by changing their order in the menu, and change the menu page order
at runtime.
- **Breaking:** Pages no longer have an `embed` parameter, as they subclass Embed and use internal methods to handle
safe handling and display.
- **Breaking:** All menu and page optional parameters have been removed in favor of methods.
- Inline comment guides in examples have been removed in favor of a small tutorial website that is being worked on.


## [0.3.5] - 2020-08-12

### Added
- Menus now accept a `destination` paramater, which takes a User or Channel object.
This will open the menu in that channel as opposed to in the current channel.

### Changed
- **Breaking:** Broke the `next` method out into two methods: `next` and `go_to`. `next` no longer
takes any parameters (previously took `name`) to jump to a different page. `go_to` acts
the same as the old `next` code, but takes a `name_or_index` parameter to accureately 
reflect the change in *0.2.8* where you could jump to indexes as well. The reason behind this
was to simplify the branching code and user readability.
- The default cancelled embed now has the title *'Cancelled'* instead of the last pages title.
- Refactored a lot of older code, particularly the subclasses of BaseMenu.
- Rewrote the README; removed the old usage sections for a simplified *'Getting Started'* section. Added in information
about new features, such as `destinations`.
- Updated to the latest discord.py version: 1.4.1
- Simplified some of the examples by removing 'fluff' code.

## [0.3.4] - 2020-07-25

### Fixed
- Fixed an issue where string-type emoji would not pass a `ButtonMenu`
check.

## [0.3.3] - 2020-07-23

*dpymenus works with Python 3.9 beta.*

### Changed
- Moved various checks into standing methods instead of lambdas for
caching opportunities.
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
- `PaginatedMenu`s now have an optional argument: `page_numbers`. If set to `True`,
embeds will generate a footer with the current and total page numbers. *This 
option will override user-defined footers.*

### Changed
- The session handler now stores sessions as a tuple `(user_id, channel_id)`
instead of just `user_id`.
- The default timeout page now has the title 'Timed Out' instead of the
last pages' name.
- **Breaking:** `set_user_inactive()` is now `close_session()`

### Fixed
- Users can now have multiple menu sessions cross-channel and guild.
- Fixed a timeout error in a `TextMenu` where it did not break after the
exception occured..
- Fixed a timeout error in all menus where it attempted to remove null data
from the session list.
- Fixed an issue where other menu buttons would call your own menu
actions. 
- Added a missing `await` in the README example for `PaginatedMenu`.

## [0.3.0] - 2020-07-17
 
### Added
- A new menu type, PaginatedMenu. See examples on how to use this feature. *`PaginatedMenu`s are very basic currently.*

- Users can now only create a single menu instance at a time in order to 
prevent abuse or confusion. *Note that if you are overriding `on_cancel` or 
`on_timeout`, you need to call `set_user_inactive()` alongside 
`self.active = False` now.*
 
### Fixed
 
- `ButtonMenu`s no longer send new messages inside DM channel types instead
of the expected default behaviour.
