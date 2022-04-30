from .gui import MYGUI
from .configer import Config
from pathlib import Path

_mybs = None

class mybs:
    def __init__(self, path=Path(__file__).parent) -> None:
        self.gui = MYGUI
        self.dir = path
        self.config = Config(self.dir)

    def run(self):
        self.gui.run(self.config)

def init() -> mybs:
    global _mybs 
    _mybs = mybs()
    return _mybs