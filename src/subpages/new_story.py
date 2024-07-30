import random as rd
import datetime as dt

import streamlit as st

from agents.screenwriter import screenwriter
from agents.role_manager import role_manager
from utils.user_info import get_new_user


need_keys = [
    "main_theme",
    "keywords",
    "worldview",
    "sex",
    "role",
    "location",
    "hp",
    "mental",
    "max_hp",
    "max_mental",
    "characteristics",
    "skills",
    "inventory",
    "start_event",
]


def get(key, default=""):
    return getattr(st.session_state, key, default)


def set(key, value, define=True):
    if not define and not hasattr(st.session_state, key):
        raise KeyError(f"st.session_state has no attribute `{key}`.")
    return setattr(st.session_state, key, value)


for k in need_keys:
    if not hasattr(st.session_state, k):
        setattr(st.session_state, k, "")

st.title("새로운 이야기")

st.text("새로운 이야기를 시작하기 앞서, 모험을 떠날 이야기를 정해봅시다.")
st.text("이야기를 정하기 위해 탐험할 세계의 주제와 세부 키워드를 입력해주세요.")

main_theme = st.text_input("세계의 주제", "좀비 아포칼립스")
keywords = st.text_input("세부 키워드", "고려 중기, 화약, 왕궁, 왕족")


if st.button("이야기 시작하기"):
    for k in need_keys:
        if get(k) == "":
            st.warning("이야기와 캐릭터를 생성한 후 결정할 수 있습니다.", icon="⚠️")
            break

    else:
        user_info = get_new_user(**{k: get(k) for k in need_keys})
        time = dt.datetime.now().strftime("%y%m%d-%H%M%S")
        st.success(
            "생성이 완료되었습니다. 페이지를 새로고침하면 좌측에 생성한 모험의 책장이 생성됩니다.",
            icon="✅",
        )


tab1, tab2 = st.tabs(["세계관 만들기", "캐릭터 설정하기"])

with tab1:
    if st.button("세계관 작성하기"):
        set("main_theme", main_theme)
        set("keywords", keywords)
        if get("main_theme") == "" or get("keywords") == "":
            st.warning("주제와 키워드를 입력하세요.")
        else:
            # gen = screenwriter.stream({"theme": get("main_theme"), "keywords": get("keywords")})
            # set("worldview", st.write_stream(gen))
            set("worldview", "테스트")

    if get("worldview") != "":
        st.write(get("worldview"))

with tab2:
    if get("worldview") == "":
        st.warning("먼저 이야기의 세계관을 결정해야 합니다.")

    else:
        charactor_keywords = st.text_input("주인공 키워드")
        st.button("재설정", type="primary")

        set("sex", rd.choice(["남성", "여성"]))
        # result = role_manager.invoke(
        #     {
        #         "worldview": get("worldview"),
        #         "charactor_keywords": charactor_keywords,
        #         "sex": get("sex"),
        #     }
        # )
        # start_info = eval(result)
        start_info = {
            "role": str(rd.randint(0, 100000)),
            "location": str(rd.randint(0, 100000)),
            "hp": rd.randint(0, 100000),
            "mental": rd.randint(0, 100000),
            "max_hp": rd.randint(0, 100000),
            "max_mental": rd.randint(0, 100000),
            "characteristics": [str(rd.randint(0, 100000))],
            "skills": [str(rd.randint(0, 100000))],
            "inventory": [str(rd.randint(0, 100000))],
            "start_event": str(rd.randint(0, 100000)),
        }
        for k, v in start_info.items():
            set(k, v, define=False)

        st.write("성별: ", get("sex"))
        st.write("역할: ", get("role"))
        st.write("위치: ", get("location"))
        st.write("현재 체력: ", get("hp"))
        st.write("현재 정신력: ", get("mental"))
        st.write("최대 체력: ", get("max_hp"))
        st.write("최대 정신력: ", get("max_mental"))
        st.write("특징: ", get("characteristics"))
        st.write("보유 기술: ", get("skills"))
        st.write("보유 아이템: ", get("inventory"))
        st.write("시작 이야기: ", get("start_event"))
