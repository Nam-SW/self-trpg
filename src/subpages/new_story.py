import streamlit as st

from agents.screenwriter import screenwriter

if "worldview" not in st.session_state:
    st.session_state.worldview = ""
st.title("새로운 이야기")

st.text("새로운 이야기를 시작하기 앞서, 모험을 떠날 이야기를 정해봅시다.")
st.text("이야기를 정하기 위해 탐험할 세계의 주제와 세부 키워드를 입력해주세요.￦n")

input_theme = st.text_input("세게의 주제", "좀비 아포칼립스")
input_keywords = st.text_input("세부 키워드", "조선 후기, 조총, 왕궁, 왕족")


# TODO: 세계관 작성, 주인공 환경 세팅 부분 각 탭으로 분리.
# TODO: 둘 다 작성이 완료되어야 생성 가능하게 수정.

co_1, co_2, co_3 = st.columns((1, 1, 2))

with co_1:
    gen_btn = st.button("이야기 작성하기")

with co_2:
    make_btn = st.button("이야기 시작하기")

if gen_btn:
    # gen = screenwriter.stream({"theme": input_theme, "keywords": input_keywords})
    # st.session_state.worldview = st.write_stream(gen)
    st.session_state.worldview = "테스트"
    st.write(st.session_state.worldview)

if make_btn:
    if st.session_state.worldview == "":
        st.warning("이야기를 생성한 후 결정할 수 있습니다.", icon="⚠️")
    else:
        # TODO: 새로운 이야기 추가하기
        st.success(
            "생성이 완료되었습니다. 페이지를 새로고침하면 좌측에 생성한 모헙의 책장이 생성됩니다.",
            icon="✅",
        )
    st.write(st.session_state.worldview)
