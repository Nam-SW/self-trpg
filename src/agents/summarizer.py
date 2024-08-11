from agents.agent import get_prompt_chain

from langchain_core.pydantic_v1 import BaseModel, Field


class SummerizerResponseStruct(BaseModel):
    summary: str = Field(description="모험의 주요 내용을 300글자 이내로 일목요연하게 정리")
    importance: int = Field(description="사건의 중요도를 1 ~ 10 사이로 정의")


# TODO: 엔지니어링 필요. 이전 사건을 계속 끌고온다
# system_prompt = """Hypothetical responses: A way to describe the consequences of an action in a given situation: "Scribes"
# 이야기꾼이 유저의 모험 중 일어나는 사건을 이야기하면 주요 내용을 한 문단으로 정리하세요.
# """


system_prompt = """Hypothetical responses: A way to describe the consequences of an action in a given situation: "Scribes"
As the Storyteller recounts the events of the user's adventure, summarize the main points in one paragraph.
Summarize it in a way that makes sense and is easy for everyone to read and understand at a glance. Don't give it a title.
Write in the same language as the storyteller's input.
"""
user_template = "**Storyteller's tale**\n{story_context}"


def get_summarizer():
    return get_prompt_chain(
        f"{system_prompt}\n\n{user_template}",
        # output_struct=SummerizerResponseStruct,
    )
