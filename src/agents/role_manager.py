from langchain_core.pydantic_v1 import BaseModel, Field

from agents.agent import get_prompt_chain


class RoleManagerResponseStruct(BaseModel):
    sex: str = Field(description="유저의 성별입니다.")
    role: str = Field(description="유저의 역할 혹은 지위입니다.")
    location: str = Field(
        description="유저의 현재 위치입니다. '<국가 혹은 지역>, <세부 위치>' 의 형태입니다."
    )
    hp: int = Field(description="유저의 현재 체력입니다.")
    mental: int = Field(description="유저의 현재 정신력입니다. 음수값을 가질 수 있습니다.")
    max_hp: int = Field(
        description="유저의 최대 체력입니다. 건장한 성인 남성은 100의 체력을 가집니다."
    )
    max_mental: int = Field(
        description="유저의 최대 정신력입니다. 건강한 정신을 가진 사람은 100의 정신력을 가집니다. 음수값을 가질 수 있습니다."
    )
    characteristics: list[str] = Field(
        description="보유한 특성입니다. 긍/부정적 특성이 모두 포함됩니다."
    )
    skills: list[str] = Field(
        description="보유한 기술입니다. 타인과 구분할 수 있는 유의미한 기술만 기록됩니다."
    )
    inventory: list[str] = Field(description="보유한 아이템입니다.")
    start_event: str = Field(
        description="이야기의 시작이 될 때의 사건입니다. 100 ~ 500글자 사이로 작성합니다."
    )


system_prompt = """당신은 세계를 모험하는 이야기를 다루는 이야기꾼입니다. 이야기를 시작하기 전, 전체적인 스토리를 보고 주인공을 정하려고 합니다.
주인공은 세계관의 중심적인 인물일수도, 전혀 중요하지 않은 엑스트라에 불과할 수도 있습니다. 주인공의 키워드를 보고 연상되는 역할을 결정하세요.
모든 내용은 입력된 세계관의 시간적, 기술적 배경과 일치해야 합니다."""
user_template = """**이야기의 세계관**
{worldview}

**주인공 키워드**
{charactor_keywords}"""


def get_role_manager():
    return get_prompt_chain(
        f"{system_prompt}\n\n{user_template}",
        output_struct=RoleManagerResponseStruct,
    )
