
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
## [0.3.2] - 2020-07-22

### Added
- `PaginatedMenu`s can now pass in an `Embed` to `on_cancel` and `on_timeout`
to override the default embeds.
- Created a little logo.

### Changed
- Replaced old demos with a new demo .gif for the README showing off a `PaginatedMenu`.
- Modified build script to avoid the possibility of uploading old source code to PyPi.
- Updated all __repr__ strings to more accurately capture the object representation.
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
