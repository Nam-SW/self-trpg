import json
import re
from typing import Any


def convert_json(text: str) -> dict:
    origin = text
    group = re.search(r"```(?:json\s*)?([\s\S]*?)```", text, re.S)
    if group is not None:
        text = group.group(1)

    try:
        text = re.search(r"(\{.+\})?", text, re.S).group()
        text = re.sub(r"\n+", " ", text)
        result = eval(text)
    except:
        try:
            result = json.loads(text)
        except:
            raise SyntaxError(f"can't convert json from context: \n{origin}")
    return result


def try_n(func: callable, args: list = [], kwargs: dict = {}, n: int = 10) -> Any:
    i = 0
    while True:
        i += 1
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            if i >= n:
                raise e
