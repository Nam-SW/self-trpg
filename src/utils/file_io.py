import json


def dump_json(file: dict, path: str) -> None:
    """json 파일 저장

    Args:
        file (dict): 저장할 json 객체
        path (str): 저장할 파일 경로
    """
    with open(path, "w") as f:
        f.write(json.dumps(file))  # 인코딩 깨지는거 방지


def load_json(path: str) -> dict:
    """json 객체 불러오기

    Args:
        path (str): 불러올 파일 경로

    Returns:
        dict: 불러온 json 객체
    """
    with open(path, "r") as f:
        data = json.load(f)
    return data


def dump_jsonl(data: list[dict], output_path: str, append: bool = False) -> None:
    """jsonl 객체 저장

    Args:
        data (list[dict]): 저장할 jsonl 객체. 각 dict object가 list로 구성됨
        output_path (str): 저장할 파일 경로
        append (bool, optional): 이미 있는 파일이라면 이어서 작성할지 여부. Defaults to False.
    """
    mode = "a+" if append else "w"
    with open(output_path, mode, encoding="utf-8") as f:
        for line in data:
            json_record = json.dumps(line, ensure_ascii=False)
            f.write(json_record + "\n")


def load_jsonl(input_path: str) -> list[dict]:
    """jsonl 객체 불러오기

    Args:
        input_path (str): 불러올 파일 경로

    Returns:
        list[dict]: 불러온 jsonl 객체
    """
    data = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line.rstrip("\n|\r")))
    return data
