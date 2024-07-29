import random as rd
import datetime as dt

import streamlit as st

from agents.screenwriter import screenwriter
from agents.role_manager import role_manager
from utils.user_info import get_new_user


need_keys = ["worldview", "sex", "role", "location", "starting_point"]
if "vars" not in st.session_state:
    st.session_state.vars = {k: "" for k in need_keys}


st.title("새로운 이야기")

st.text("새로운 이야기를 시작하기 앞서, 모험을 떠날 이야기를 정해봅시다.")
st.text("이야기를 정하기 위해 탐험할 세계의 주제와 세부 키워드를 입력해주세요.￦n")

# TODO: 얘네들도 변수로 추가해야함
input_theme = st.text_input("세게의 주제", "좀비 아포칼립스")
input_keywords = st.text_input("세부 키워드", "조선 후기, 조총, 왕궁, 왕족")


if st.button("이야기 시작하기"):
    st.write(str(st.session_state.vars))

    for k in need_keys:
        if st.session_state.vars[k] == "":
            st.warning("이야기를 생성한 후 결정할 수 있습니다.", icon="⚠️")
            break

    else:
        user_info = get_new_user(*[st.session_state.vars[k] for k in need_keys])
        fn = dt.datetime.now().strftime("%y%m%d-%H%M%S_")
        st.success(
            "생성이 완료되었습니다. 페이지를 새로고침하면 좌측에 생성한 모험의 책장이 생성됩니다.",
            icon="✅",
        )


tab1, tab2 = st.tabs(["세계관 만들기", "캐릭터 설정하기"])

with tab1:
    if st.button("이야기 작성하기"):
        # gen = screenwriter.stream({"theme": input_theme, "keywords": input_keywords})
        # st.session_state.vars['worldview'] = st.write_stream(gen)
        st.session_state.vars["worldview"] = "테스트"
    if st.session_state.vars["worldview"] != "":
        st.write(st.session_state.vars["worldview"])

with tab2:
    if st.session_state.vars["worldview"] == "":
        st.warning("먼저 이야기의 세계관을 결정해야 합니다.")

    else:
        col1, col2 = st.columns(2)
        with col1:
            set_rand_btn = st.button("랜덤으로 설정하기")
        with col2:
            decision_btn = st.button("결정하기")

        sex = st.empty()
        role_ti = st.empty()
        location_ti = st.empty()
        starting_point_ti = st.empty()

        sex_dict = {0: "남성", 1: "여성"}
        sex_idx = 0
        if set_rand_btn:
            sex_idx = rd.randint(0, 1)
            # gen = role_manager.invoke({"worldview": st.session_state.vars['worldview'], "sex": sex_dict[sex_idx]})
            # start_info = eval(gen)
            start_info = {
                "user_role": "역할 테스트",
                "current_location": "위치 테스트",
                "start_event": "시작 테스트",
            }
            st.session_state.vars["sex"] = sex_dict[sex_idx]
            st.session_state.vars["role"] = start_info["user_role"]
            st.session_state.vars["location"] = start_info["current_location"]
            st.session_state.vars["starting_point"] = start_info["start_event"]

        sex.selectbox("캐릭터의 성별", sex_dict.values(), index=sex_idx, key="sex_widget")
        role_ti.text_input("캐릭터 직업", st.session_state.vars["role"], key="role_widget")
        location_ti.text_input(
            "캐릭터의 현재 위치", st.session_state.vars["location"], key="location_widget"
        )
        starting_point_ti.text_input(
            "이야기 시작 시 시점",
            st.session_state.vars["starting_point"],
            key="starting_point_widget",
        )

        if decision_btn:
            # 수동으로 설정했을 때 위해서
            st.session_state.vars["sex"] = st.session_state.sex_widget
            st.session_state.vars["role"] = st.session_state.role_widget
            st.session_state.vars["location"] = st.session_state.location_widget
            st.session_state.vars["starting_point"] = st.session_state.starting_point_widget
