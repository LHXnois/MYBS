import json
import os
from pydantic import BaseModel
class Config(BaseModel):
    path: str

    def save(self):
        try:
            
            with open(self.path, 'w', encoding='utf8') as f:
                json.dump(self.dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as ex:
            return False

def initconfig(path) -> Config:
    if os.path.exists(path):
        return Config(load_jsons(path))
    else:
        return Config(**{
            'path': path
        })


def load_jsons(path: str) -> dict:
    try:
        with open(path, mode='r', encoding='utf8') as f:
            data = json.load(f)
            return data
    except Exception as ex:
        return {}