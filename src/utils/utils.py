import json


def convert_json(text: str) -> dict:
    try:
        result = eval(text)
    except:
        result = json.loads(text)
    return result
