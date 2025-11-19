class WatchdogError(Exception):
    def __init__(self, name:str, *args):
        super().__init__(*args)
        self.name = name

class WatchdogWarning(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

class Watchdog():
    __store: dict[str, int]
    def __init__(self):
        self.__store = {}

    def start(self, name: str, max: int = 10):
        self.__store[name] = max

    def update(self, name: str):
        if name in self.__store.keys():
            newval = self.__store[name] - 1
            self.__store[name] = newval
            if newval < 0:
                raise WatchdogWarning(f'Watchdog for "{name}" was called without being reset')
            if newval <= 0:
                raise WatchdogError(name)
        else:
            raise WatchdogWarning(f'Watchdog for "{name}" has not been started')

monitor = Watchdog()
