from .util import load_jsons, save_jsons
from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    rootpath: str
    suoyin: bool = False

    def __init__(__pydantic_self__, path: Path) -> None:
        data = load_jsons(path.joinpath('data', 'config.json'), 
                          default={
                              'rootpath': path.resolve().__str__(),
                              })
        try:
            super().__init__(**data)
        except:
            print('配置文件损坏！')

    def save(self) -> bool:
        return save_jsons(self.path, self.dict())

    @property
    def fdpath(self) -> Path:
        return Path(self.rootpath).joinpath('data', 'fdata.json')

    @property
    def path(self) -> Path:
        return Path(self.rootpath).joinpath('data', 'config.json')
