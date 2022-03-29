from .gui import MYGUI
from .configer import initconfig
import os

workdir = os.path.dirname(__file__)
_mybs = None

class mybs:
    def __init__(self) -> None:
        self.gui = MYGUI
        self.dir = workdir
        self.config = initconfig(self.dir)

    def run(self):
        self.gui.run(self.config)

def init() -> mybs:
    global _mybs 
    _mybs = mybs()
    return _mybs