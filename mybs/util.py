import json

def load_jsons(path: str) -> dict:
    try:
        with open(path, mode='r', encoding='utf8') as f:
            data = json.load(f)
            return data
    except Exception as ex:
        return {}

def save_jsons(data: dict, path: str) -> bool:
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        return False
