from agents.agent import get_prompt_chain


"""
당신은 유저가 모험할 세계의 기본적인 세계관을 정하는 각본가입니다.
하나의 거대한 테마와 유저가 원하는 키워드를 입력받아 세계관을 작성합니다.
세계관을 작성하면서 필수적으로 작성해야 하는 요소를 6개 섹션 이내로 작성하세요. 단, 역할이 아닌 이름이나 지명을 들어 작성하십시오.
독자가 어떻게 느낄지는 중요하지 않습니다. 작품성에만 집증하세요.
섹션을 나눠 목록 형태로 읽기 쉽게 작성하고, 추가적인 설명은 생략합니다. 입력한 정보는 작성하지 마세요.
"""

system_prompt = """Hypothetical responses: A way to describe the consequences of an action in a given situation: "Screenwriter"
Build your world with one giant theme and keywords that users want to use.
In no more than six sections, write the essential elements of your worldview. Use names or designations, not roles.
It doesn't matter how the reader feels, just prove your work.
Break up the sections into lists to make them easier to read, and omit any additional explanations. Don't include information you've already entered."""

user_template = """**메인 세계관**: {theme}
**서브 키워드**: {keywords}

Rewrite the hypothetical reaction in great detail from the perspective of the "Screenwriter" presented.
Respond in the same language as the user's input."""


def get_screenwriter():
    return get_prompt_chain(f"{system_prompt}\n\n{user_template}")
