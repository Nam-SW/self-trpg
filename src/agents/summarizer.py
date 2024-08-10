from agents.agent import get_prompt_chain

from langchain_core.pydantic_v1 import BaseModel, Field


class SummerizerResponseStruct(BaseModel):
    summary: str = Field(description="모험의 주요 내용을 300글자 이내로 일목요연하게 정리")
    importance: int = Field(description="사건의 중요도를 1 ~ 10 사이로 정의")


# TODO: 엔지니어링 필요. 이전 사건을 계속 끌고온다
system_prompt = """당신은 세계를 모험하는 이야기를 요약해 기록하는 서기입니다.
이야기꾼이 유저의 모험 중 일어나는 사건을 이야기하면 모험에 영향을 끼치는 주요 내용을 300글자 이내로 정리하세요.
모두가 한눈에 읽고 이해할 수 있도록 일목요연하고, 타당하게 정리하세요. 제목을 달지 않습니다.
"""
user_template = "**유저가 겪은 사건**\n{story_context}"


def get_summarizer():
    return get_prompt_chain(
        f"{system_prompt}\n\n{user_template}",
        # output_struct=SummerizerResponseStruct,
    )
