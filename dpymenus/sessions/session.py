from typing import TYPE_CHECKING, TypeVar, Union

from discord import Member, User

if TYPE_CHECKING:
    from dpymenus import TextMenu, ButtonMenu, PaginatedMenu, Poll

    Menu = TypeVar("Menu", TextMenu, ButtonMenu, PaginatedMenu, Poll)


class Session:
    def __init__(self, owner: Union[Member, User], instance: "Menu"):
        self.owner = owner
        self.instance = instance
        self.active = True

    def kill(self):
        pass
