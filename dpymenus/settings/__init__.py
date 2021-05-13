import logging
import os
from pathlib import Path

import toml

from dpymenus.exceptions import ButtonsError


def load_settings():
    """Attempts to parse a pyproject.toml file and get all data under the [dpymenus] header."""
    data = {}

    try:
        with open(Path(os.getcwd()) / 'pyproject.toml', 'r') as file:
            data = toml.load(file)
            logging.info('Found pyproject.toml; loading data...')
    except FileNotFoundError:
        logging.info(
            '''Could not find a pyproject.toml file with a valid [dpymenus] header. Using default settings.
            See https://github.com/robertwayne/dpymenus#configuration on how to set configuration options.'''
        )
    finally:
        config_data = data.get('dpymenus', {})

        return config_data if config_data else {}


config = load_settings()

# set global menu settings
HISTORY_CACHE_LIMIT = config.get('history-cache-limit', 10)
SESSION_PER_CHANNEL_LIMIT = config.get('sessions-per-channel', 1)
SESSION_PER_GUILD_LIMIT = config.get('sessions-per-guild', 3)
SESSION_PER_USER_LIMIT = config.get('sessions-per-user', 10)
SESSION_TIMEOUT = config.get('session-timeout', 3600)
ALLOW_SESSION_RESTORE = config.get('allow-session-restore', False)
HIDE_WARNINGS = config.get('hide-warnings', False)
REPLY_AS_DEFAULT = config.get('reply-as-default', False)
BUTTON_DELAY = config.get('button-delay', 0.35)
TIMEOUT = config.get('timeout', 120)

# set constants
CONSTANTS_CONFIRM = config.get(
    'constants-confirm', ['y', 'yes', 'ok', 'k', 'kk', 'ready', 'rdy', 'r', 'confirm', 'okay']
)
CONSTANTS_DENY = config.get('constants-deny', ['n', 'no', 'deny', 'negative', 'back', 'return'])
CONSTANTS_QUIT = config.get('constants-quit', ['e', 'exit', 'q', 'quit', 'stop', 'x', 'cancel', 'c'])
CONSTANTS_BUTTONS = config.get('constants-buttons', ['⏮️', '◀️', '⏹️', '▶️', '⏭️'])

if len(CONSTANTS_BUTTONS) < 3:
    raise ButtonsError(
        '`constants-buttons` in pyproject.toml must have 3 to 5 values to cover all default cases. '
        'Partial overwrites are not allowed. See '
        'https://github.com/robertwayne/dpymenus-book#constants for more information.'
    )
