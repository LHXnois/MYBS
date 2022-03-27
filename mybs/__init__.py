from .gui import MYGUI
from .configer import initconfig
import os

workdir = os.path.dirname(__file__)
_mybs = None

class mybs:
    def __init__(self) -> None:
        self.gui = MYGUI
        self.config = initconfig(os.path.join(workdir, 'data', 'config.json'))
        self.dir = workdir

    def run(self):
        self.gui.run(self.config)

def init() -> mybs:
    _mybs = mybs()
    os.makedirs(os.path.join(workdir, 'data'), exist_ok=True)
    return _mybs