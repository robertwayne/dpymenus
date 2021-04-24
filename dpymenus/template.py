from dataclasses import dataclass
from discord import Embed

@dataclass
class Template:
    title: str = None
    description: str = None
    color: str = None
    footer: dict = None
    image: str = None
    url: str = None
    thumbnail: str = None
    author: dict = None
