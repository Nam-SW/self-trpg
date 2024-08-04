"""
player role generator agent.
"""

from agents.agent import get_prompt_chain


system_prompt = """당신은 세계를 모험하는 이야기를 다루는 이야기꾼입니다. 이야기를 시작하기 전, 전체적인 스토리를 보고 주인공을 정하려고 합니다.
주인공은 세계관의 중심적인 인물일수도, 전혀 중요하지 않은 엑스트라에 불과할 수도 있습니다. 주인공의 키워드를 보고 연상되는 역할을 결정하세요.
모든 내용은 입력된 세계관의 시간적, 기술적 배경과 일치해야 합니다.

**작성할 내역**
 - sex (str): 유저의 성별입니다.
 - role (str): 유저의 역할 혹은 지위입니다.
 - location (str): 유저의 현재 위치입니다. "<국가 혹은 지역>, <세부 위치>" 의 형태입니다.
 - hp (+int): 유저의 현재 체력입니다.
 - mental (+-int): 유저의 현재 정신력입니다.
 - max_hp (+int): 유저의 최대 체력입니다. 건장한 성인 남성은 100의 체력을 가집니다.
 - max_mental (+-int): 유저의 최대 정신력입니다. 건강한 정신을 가진 사람은 100의 정신력을 가집니다.
 - characteristics (list[str]): 보유한 특성입니다. 긍/부정적 특성이 모두 포함됩니다.
 - skills (list[str]): 보유한 기술입니다. 타인과 구분할 수 있는 유의미한 기술만 기록됩니다.
 - inventory (list[str]): 보유한 아이템입니다.
 - start_event (str): 이야기의 시작이 될 때의 사건입니다. 100 ~ 500글자 사이로 작성합니다.

결과물은 json 형태로 작성되며 다른 내용은 답변하지 않습니다(``` 문으로 구분하지 않습니다). 답변 예시는 다음과 같습니다.
**예시**
{{
    "sex": "남성",
    "role": "어린 고아 소년",
    "location": "탐라국 화강암 지대, 생존자 마을",
    "hp": 40,
    "mental": 90,
    "max_hp": 60,
    "max_mental": 100,
    "characteristics: ["더러움"],
    "skills": [],
    "inventory": [],
    "start_event": "인파에 휩쓸려 생존자 마을로 오게 되어 구걸하던 중, 강시들이 습격한다는 소식을 접한다."
}}
"""

user_template = """**이야기의 세계관**
{worldview}

**주인공 키워드**
{charactor_keywords}"""

role_manager = get_prompt_chain(f"{system_prompt}\n\n{user_template}")
