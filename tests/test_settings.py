from dpymenus import settings
from dpymenus.settings import HISTORY_CACHE_LIMIT


def test_load_settings():
    config = settings.load_settings()
    assert isinstance(config, dict)
    assert HISTORY_CACHE_LIMIT == 10
