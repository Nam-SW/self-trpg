from agents.agent import get_prompt_chain

from langchain_core.pydantic_v1 import BaseModel, Field


class SummerizerResponseStruct(BaseModel):
    summary: str = Field(description="모험의 주요 내용을 500글자 이내로 일목요연하게 정리")
    importance: int = Field(description="사건의 중요도를 1 ~ 10 사이로 정의")


# TODO: 엔지니어링 필요. 이전 사건을 계속 끌고온다
system_prompt = """당신은 세계를 모험하는 이야기를 요약해 기록하는 서기입니다.
이야기꾼이 유저의 모험 중 일어나는 사건을 이야기하면 모험에 영향을 끼치는 주요 내용을 500글자 이내로 정리해 기록하며, 해당 이야기의 중요도를 판단합니다.
모두가 한눈에 읽고 이해할 수 있도록 일목요연하고, 타당하게 정리하세요.

중요도 기준
1 ~ 2 - 유저와 주변 동료에 영향을 미침
3 ~ 4 - 마을 단위에 영향을 미침
5 ~ 6 - 지역 단위에 영향을 미침
7 ~ 8 - 국가 단위에 영향을 미침
9 ~ 10 - 세계 전역에 영향을 미침"""
user_template = "**유저가 겪은 사건**\n{story_context}"

summarizer = get_prompt_chain(
    f"{system_prompt}\n\n{user_template}",
    output_struct=SummerizerResponseStruct,
)
