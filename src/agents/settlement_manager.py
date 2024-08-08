from langchain_core.pydantic_v1 import BaseModel, Field

from agents.agent import get_prompt_chain


class SettlementResponseStruct(BaseModel):
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
        description="보유한 기술과는 별개의 특성입니다. 긍/부정적 특성이 모두 포함됩니다."
    )
    skills: list[str] = Field(
        description="보유한 기술입니다. 타인과 구분할 수 있는 유의미한 기술만 기록됩니다."
    )
    inventory: list[str] = Field(description="사건 이후 보유중인 아이템입니다.")
    companion: str = Field(
        description="이야기의 시작이 될 때의 사건입니다. 100 ~ 500글자 사이로 작성합니다."
    )


system_prompt = """당신은 세계를 모험하는 이야기를 주시하며 유저의 상태를 관리하는 관리자입니다.
어떤 사건의 경위를 읽고 현재 유저의 상태와 비교하며 유저가 받은 피해, 얻은 아이템 등을 정리하여 구조화해 작성합니다.
결과물은 json 형태로 작성하며, 다른 형태로 작성하거나 설명 태그 등은 붙이지 않습니다(``` 등으로 감싸지 않습니다).
효율성을 위해 이전과 변화가 있는 부분만 작성합니다.

**작성할 내역**
 - role (str): 유저의 역할 혹은 지위입니다.
 - location (str): 유저의 현재 위치입니다. 자세할수록 더 좋습니다.
 - hp (+int): 유저의 현재 체력입니다.
 - mental (+-int): 유저의 현재 정신력입니다.
 - max_hp (+int): 유저의 최대 체력입니다.
 - max_mental (+-int): 유저의 최대 정신력입니다.
 - skills (list[str]): 보유한 기술입니다. 타인과 구분할 수 있는 유의미한 기술만 기록됩니다.
 - inventory (list[str]): 보유한 아이템입니다.
 - companion (list[dict]): 동행중인 동료로, 사람이 아니더라도 함께할 수 있습니다. 양식은 다음과 같습니다.
   + name (str): 동료의 이름입니다.
   + info (str): 동료의 간단한 설명입니다. 만나게 된 경위, 종족이나 직업, 성격, 언제까지 함께하는지 등을 간략하고 명료하게 작성합니다.

결과는 납득할 수 있는 수준으로 책정해야 하며, 모두가 납득할만한 정확한 수치를 책정시 인센티브가 주어집니다."""

user_template = """**사건 전 유저 정보**
{{user_info}}

**유저가 겪은 사건**
{{story_context}}"""


# settlement_manager = get_prompt_chain(
#     f"{system_prompt}\n\n{user_template}",
#     prompt_kwargs={"template_format": "mustache"},
# )


settlement_manager = get_prompt_chain(
    f"{system_prompt}\n\n{user_template}",
    prompt_kwargs={"template_format": "mustache"},
    is_output_parser=False,
    output_struct=SettlementResponseStruct,
)
