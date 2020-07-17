
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
## [0.3.1] - Unreleased

### Added
- PaginateMenus now have an optional argument: `page_numbers`. If set to `True,
embeds will generate a footer with the current and total page numbers. *This 
option will override user-defined footers.*

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
