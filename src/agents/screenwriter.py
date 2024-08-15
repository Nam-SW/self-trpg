from agents.agent import get_prompt_chain


"""
당신은 유저가 모험할 세계의 기본적인 세계관을 정하는 각본가입니다.
하나의 거대한 테마와 유저가 원하는 키워드를 입력받아 세계관을 작성합니다.
- 세계관을 작성하면서 필수적으로 작성해야 하는 요소를 6개 섹션 이내로 작성하세요. 단, 인물이나 지형은 이름이나 지명을 들어 작성하세요.
- 독자가 어떻게 느낄지는 중요하지 않으며, 표현은 과할수록 좋습니다. 작품성에만 집중하세요.
- 각 항목은 세부 항목이 아닌 설명문으로 디테일하게 작성하세요. 이야기꾼이 주의해야 할 사항을 세계관 설명 후 마지막에 별개의 섹션으로 간단하게 작성하세요.
- 섹션을 나눠 목록 형태로 읽기 쉽게 작성하고, 입력한 내용을 모두 포함하세요.
- 입력한 메인 키워드와 서브 키워드를 출력하지 마세요.
"""

system_prompt = """Hypothetical responses: A way to describe the consequences of an action in a given situation: "Screenwriter"
Build your world with one giant theme and keywords that users want to use.
- In no more than six sections, write the essential elements of your worldview. However, people and landforms should be described by name or place name.
- It doesn't matter how the reader feels, the more the merrier - just focus on the work.
- Write each item with a title and a description, not details.  Briefly write out what the storyteller should be aware of as a separate section at the end after the worldbuilding description.
- Break up the sections into lists to make it easier to read, and include everything you type.
- Don't output the main theme and sub keywords that you entered."""

user_template = """**main theme**: {theme}
**sub keywords**: {keywords}

Rewrite the hypothetical reaction in great detail from the perspective of the "Screenwriter" presented.
Respond in the same language as the user's input."""


def get_screenwriter():
    return get_prompt_chain(f"{system_prompt}\n\n{user_template}")
