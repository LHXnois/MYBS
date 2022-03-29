from .util import load_jsons, save_jsons
import os
from pydantic import BaseModel

class Config(BaseModel):
    rootpath: str
    fdpath: str
    suoyin: bool = False
    def __init__(__pydantic_self__, path) -> None:
        data = load_jsons(os.path.join(path, 'data', 'config.json'))
        data.setdefault('fdpath', os.path.join(data['rootpath'], 'data', 'fdata.json'))
        try:
            super().__init__(**data)
        except:
            print('配置文件损坏！')

    def save(self):
        return save_jsons(self.dict(), self.path)

def initconfig(path) -> Config:
    os.makedirs(os.path.join(path, 'data'), exist_ok=True)
    if os.path.exists(path):
        save_jsons({
            'rootpath': path
        }, os.path.join(path, 'data', 'config.json'))
    return Config(path)
