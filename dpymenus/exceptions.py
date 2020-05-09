class MenuError(Exception):
    def __init__(self, message):
        self.message = message


class PagesError(MenuError):
    pass


class ButtonsError(MenuError):
    pass
