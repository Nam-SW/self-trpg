# import random as rd

import streamlit as st

from agents.screenwriter import get_screenwriter
from agents.role_manager import get_role_manager
from utils.user_info import get_new_user, save_story


screenwriter = get_screenwriter()
role_manager = get_role_manager()

if not hasattr(st.session_state, "info"):
    st.session_state["info"] = {
        "main_theme": "",
        "keywords": "",
        "worldview": "",
        "limit_event": "",
        "role": "",
        "sex": "",
        "location": "",
        "hp": "",
        "mental": "",
        "max_hp": "",
        "max_mental": "",
        "characteristics": "",
        "skills": "",
        "inventory": "",
        "start_event": "",
    }


st.title("새로운 이야기")

st.text("새로운 이야기를 시작하기 앞서, 모험을 떠날 이야기를 정해봅시다.")
st.text("이야기를 정하기 위해 탐험할 세계의 주제와 세부 키워드를 입력해주세요.")

story_name = st.text_input("이야기의 이름", placeholder="ex) 좀비고려")
main_theme = st.text_input("세계의 주제", placeholder="ex) 좀비(강시) 아포칼립스")
keywords = st.text_area("세부 키워드", placeholder="ex) 강시 역병, 고려 중기, 화약, 왕궁, 왕족")
limit_event = st.slider("이야기의 길이", 10, 200, 50)


if st.button("이야기 시작하기"):
    st.session_state["info"]["limit_event"] = limit_event
    if "" in st.session_state["info"].values():
        st.warning("이야기와 캐릭터를 생성한 후 결정할 수 있습니다.", icon="⚠️")

    else:
        user_info = get_new_user(**st.session_state["info"])
        save_story(st.session_state["username"], user_info, story_name)
        st.success(
            "생성이 완료되었습니다. 페이지를 새로고침하면 좌측에 생성한 모험의 책장이 생성됩니다.",
            icon="✅",
        )


tab1, tab2 = st.tabs(["세계관 만들기", "캐릭터 설정하기"])

with tab1:
    if st.button("세계관 작성하기"):
        st.session_state["info"]["main_theme"] = main_theme
        st.session_state["info"]["keywords"] = keywords
        if (
            st.session_state["info"]["main_theme"] == ""
            or st.session_state["info"]["keywords"] == ""
        ):
            st.warning("주제와 키워드를 입력하세요.")
        else:
            worldview = screenwriter.invoke(
                {
                    "theme": st.session_state["info"]["main_theme"],
                    "keywords": st.session_state["info"]["keywords"],
                }
            )
            st.session_state["info"]["worldview"] = worldview
            st.write(worldview)
            # st.session_state["info"]["worldview"] = "테스트")

    # if st.session_state["info"]["worldview") != "":
    #     st.write(st.session_state["info"]["worldview"))

with tab2:
    if st.session_state["info"]["worldview"] == "":
        st.warning("먼저 이야기의 세계관을 결정해야 합니다.")

    else:
        charactor_keywords = st.text_input("주인공 키워드")
        if st.button("재설정"):

            # st.session_state["info"]["sex"] = rd.choice(["남성", "여성"]))
            start_info = role_manager.invoke(
                {
                    "worldview": st.session_state["info"]["worldview"],
                    "charactor_keywords": charactor_keywords,
                    # "sex": st.session_state["info"]["sex"),
                }
            )
            # start_info = convert_json(result)

            # start_info = {
            #     "sex": str(rd.randint(0, 100000)),
            #     "role": str(rd.randint(0, 100000)),
            #     "location": str(rd.randint(0, 100000)),
            #     "hp": rd.randint(0, 100000),
            #     "mental": rd.randint(0, 100000),
            #     "max_hp": rd.randint(0, 100000),
            #     "max_mental": rd.randint(0, 100000),
            #     "characteristics": [str(rd.randint(0, 100000))],
            #     "skills": [str(rd.randint(0, 100000))],
            #     "inventory": [str(rd.randint(0, 100000))],
            #     "start_event": str(rd.randint(0, 100000)),
            # }

            for k, v in start_info.items():
                st.session_state["info"][k] = v
            st.write("성별: ", st.session_state["info"]["sex"])
            st.write("역할: ", st.session_state["info"]["role"])
            st.write("위치: ", st.session_state["info"]["location"])
            st.write("현재 체력: ", st.session_state["info"]["hp"])
            st.write("현재 정신력: ", st.session_state["info"]["mental"])
            st.write("최대 체력: ", st.session_state["info"]["max_hp"])
            st.write("최대 정신력: ", st.session_state["info"]["max_mental"])
            st.write("특성: ", st.session_state["info"]["characteristics"])
            st.write("보유 기술: ", st.session_state["info"]["skills"])
            st.write("보유 아이템: ", st.session_state["info"]["inventory"])
            st.write("시작 이야기: ", st.session_state["info"]["start_event"])
