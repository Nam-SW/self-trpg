# import random as rd

import streamlit as st

from agents.screenwriter import get_screenwriter, world_to_document
from agents.role_manager import get_role_manager
from story_info import StoryInfoManager


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
        "prev_summary": "",
    }


st.title("새로운 이야기")

form = st.form(key="story_form")
form.write("새로운 이야기를 시작하기 앞서, 모험을 떠날 이야기를 정해봅시다.")
form.write("이야기를 정하기 위해 탐험할 세계의 주제와 세부 내용을 입력해주세요.")

story_name = form.text_input("이야기의 제목")
limit_event = form.slider("이야기의 길이", 10, 200, 50)


if form.form_submit_button("이야기 시작하기"):
    st.session_state["info"]["limit_event"] = limit_event
    if "" in st.session_state["info"].values():
        st.warning("이야기와 캐릭터를 생성한 후 결정할 수 있습니다.", icon="⚠️")

    else:
        story = StoryInfoManager(
            st.session_state["username"], story_name, **st.session_state["info"]
        )
        story.save()
        st.success(
            "생성이 완료되었습니다. 페이지를 새로고침하면 좌측에 생성한 모험의 책장이 생성됩니다.",
            icon="✅",
        )


tab1, tab2 = st.tabs(["세계관 만들기", "캐릭터 설정하기"])

with tab1:
    worldview_form = st.form(key="worldview_form")
    main_theme = worldview_form.text_input("세계의 주제", placeholder="ex) 좀비(강시) 아포칼립스")
    requirements = worldview_form.text_area(
        "세부 내용", placeholder="ex) 강시 역병, 고려 중기, 화약, 왕궁, 왕족"
    )

    if worldview_form.form_submit_button("이야기 작성하기"):
        st.session_state["info"]["main_theme"] = main_theme
        st.session_state["info"]["requirements"] = requirements
        if (
            st.session_state["info"]["main_theme"] == ""
            or st.session_state["info"]["requirements"] == ""
        ):
            st.warning("주제와 세부 내용을 입력하세요.")
        else:
            with st.spinner("이야기를 쓰는 중입니다..."):
                worldview = screenwriter.invoke(
                    {
                        "theme": st.session_state["info"]["main_theme"],
                        "requirements": st.session_state["info"]["requirements"],
                    }
                )
            st.session_state["info"]["worldview"] = worldview
    if isinstance(st.session_state["info"]["worldview"], dict):
        # st.write(st.session_state["info"]["worldview"])
        st.markdown(world_to_document(st.session_state["info"]["worldview"]))

with tab2:
    if st.session_state["info"]["worldview"] == "":
        st.warning("먼저 이야기의 세계관을 결정해야 합니다.")

    else:
        start_form = st.form(key="start_form")
        charactor_keywords = start_form.text_input("주인공 키워드", placeholder="ex) 남성, 부랑자")

        if start_form.form_submit_button("이야기 작성하기"):
            with st.spinner("주인공을 정하는 중입니다..."):
                start_info = role_manager.invoke(
                    {
                        # "worldview": st.session_state["info"]["worldview"],
                        "worldview": world_to_document(st.session_state["info"]["worldview"]),
                        "charactor_keywords": charactor_keywords,
                    }
                )

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
            st.write("시작 이야기: ", st.session_state["info"]["prev_summary"])
