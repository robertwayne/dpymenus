
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
## [0.2.10] - 2020-07-17
  
`pip install dpymenus==0.2.10`
 
### Added
- Users can now only create a single menu instance at a time in order to 
prevent abuse or confusion. 

      Note that if you are overriding `on_cancel` or
      `on_timeout`, you need to call `set_user_inactive()` alongside 
      `self.active = False` now.
 
### Fixed
 
- ButtonMenus no longer send new messages inside DM channel types instead
of the expected default behaviour.
