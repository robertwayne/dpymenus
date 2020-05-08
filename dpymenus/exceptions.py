class MenuError(Exception):
    def __init__(self, message):
        self.message = message


class NotEnoughPagesError(MenuError):
    pass


class NoButtonsError(MenuError):
    pass
