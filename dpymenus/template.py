from dataclasses import dataclass


@dataclass
class Template:
    title: str
    description: str
    color: str
    footer: str
