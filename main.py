from gui import MYGUI
from configer import initconfig
from os import path
if __name__ == '__main__':
    config = initconfig(path.join(path.dirname(__file__), 'data', 'config.json'))
    config.save()
    MYGUI.run()