import os
from pathlib import Path
import toml
import logging


try:
    with open(Path(os.getcwd()) / 'pyproject.toml', 'r') as file:
        data = toml.load(file)
        config = data.get('dpymenus', {})
except FileNotFoundError:
    logging.info(
        '''
        Could not find a pyproject.toml file with a valid [dpymenus] header. Using default settings.
        See https://github.com/robertwayne/dpymenus#configuration on how to set configuration options.
        '''
    )
finally:
    HISTORY_CACHE_LIMIT = config.get('history-cache-limit', 10)
    SESSION_PER_CHANNEL_LIMIT = config.get('sessions-per-channel', 1)
    SESSION_PER_GUILD_LIMIT = config.get('sessions-per-guild', 3)
    SESSION_PER_USER_LIMIT = config.get('sessions-per-user', 10)
    SESSION_TIMEOUT = config.get('session-timeout', 3600)

    ALLOW_SESSION_RESTORE = config.get('allow-session-restore', True)
    HIDE_WARNINGS = config.get('hide-warnings', False)
    PREVENT_MULTISESSIONS = config.get('prevent-multisessions', False)

    REPLY_AS_DEFAULT = config.get('reply-as-default', True)

    COGWATCH_INTEGRATION = config.get('cogwatch-integration', False)
