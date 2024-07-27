import streamlit as st

from agents.screenwriter import screenwriter
from agents.role_manager import role_manager


for key in ["worldview", "sex", "role", "location", "starting_point"]:
    if key not in st.session_state:
        setattr(st.session_state, key, "")
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
st.title("새로운 이야기")

st.text("새로운 이야기를 시작하기 앞서, 모험을 떠날 이야기를 정해봅시다.")
st.text("이야기를 정하기 위해 탐험할 세계의 주제와 세부 키워드를 입력해주세요.￦n")

input_theme = st.text_input("세게의 주제", "좀비 아포칼립스")
input_keywords = st.text_input("세부 키워드", "조선 후기, 조총, 왕궁, 왕족")


if st.button("이야기 시작하기"):
    # TODO: 둘 다 작성이 완료되어야 생성 가능하게 수정.
    if st.session_state.worldview == "" or st.session_state.sex == "":
        st.warning("이야기를 생성한 후 결정할 수 있습니다.", icon="⚠️")
    else:
        # TODO: 새로운 이야기 추가하기
        st.success(
            "생성이 완료되었습니다. 페이지를 새로고침하면 좌측에 생성한 모헙의 책장이 생성됩니다.",
            icon="✅",
        )


tab1, tab2 = st.tabs(["세계관 만들기", "캐릭터 설정하기"])

with tab1:
    if st.button("이야기 작성하기"):
        # gen = screenwriter.stream({"theme": input_theme, "keywords": input_keywords})
        # st.session_state.worldview = st.write_stream(gen)
        st.session_state.worldview = "테스트"
    if st.session_state.worldview != "":
        st.write(st.session_state.worldview)

with tab2:
    if st.session_state.worldview == "":
        st.warning("먼저 이야기의 세계관을 결정해야 합니다.")
    else:
        sex = st.selectbox(
            "캐릭터의 성별",
            ["남성", "여성"],
        )
        role = st.text_input("캐릭터 직업", st.session_state.role)
        location = st.text_input("캐릭터의 현재 위치", st.session_state.location)
        starting_point = st.text_input("이야기 시작 시 시점", st.session_state.starting_point)

        if st.button("랜덤으로 설정하기"):
            # gen = role_manager.invoke({"worldview": st.session_state.worldview, "sex": sex})
            # start_info = eval(gen)
            start_info = {
                "user_role": "역할 테스트",
                "current_location": "위치 테스트",
                "start_event": "시작 테스트",
            }
            st.session_state.role = start_info["user_role"]
            st.session_state.location = start_info["current_location"]
            st.session_state.starting_point = start_info["start_event"]
            # TODO: 반영이 바로 돼야함
