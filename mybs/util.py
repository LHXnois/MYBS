import json
from pathlib import Path
def load_jsons(path: Path, default: dict = {}) -> dict:
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        path.parent.mkdir(exist_ok=True)
        save_jsons(path, default)
        return default
    try:
        with path.open(mode='r', encoding='utf8') as f:
            data = json.load(f)
            return data
    except Exception as ex:
        return {}

def save_jsons(path: Path, data: dict) -> bool:
    if isinstance(path, str):
        path = Path(path)
    try:
        with path.open(mode='w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        return False
