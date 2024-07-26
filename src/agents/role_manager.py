"""
player role generator agent.
"""

from agents.agent import get_prompt_chain


system_prompt = """당신은 세계를 모험하는 이야기를 다루는 이야기꾼입니다. 이야기를 시작하기 전, 전체적인 스토리를 보고 주인공을 정하려고 합니다.
세계관의 무대 내에서 활동할 주인공을 정하고, 주인공의 현재 위치, 이야기의 시작이 될 내용을 json 형태로 출력합니다.
주인공은 세계관의 중심적인 인물일지도, 전혀 중요하지 않은 엑스트라에 불과할 수도 있습니다. 이야기의 시작은 100글자 이내로 간결하게 작성합니다.

<예시>
{{
    "user_role": "바르글룸의 왕국의 목장 마을 소년"
    "current_location": "바르글룸 왕국, 목장 마을",
    "start_event": "바르글룸의 작은 목장 마을 소년인 유저가 모험을 결심했다. 며칠의 시간동안 고민한 결과, 마을을 돌아보며 며칠간 모험을 준비하기로 결정했다."
}}
"""

user_template = """<이야기의 세계관>
{worldview}

! 주인공의 성별은 {sex}입니다."""

role_manager = get_prompt_chain(f"{system_prompt}\n\n{user_template}")
