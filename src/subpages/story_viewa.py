import streamlit as st


from agents.screenwriter import screenwriter
from agents.role_manager import role_manager
from agents.storyteller import storyteller
from agents.story_closer import story_closer
from agents.summarizer import summarizer
from agents.settlement_manager import settlement_manager

from utils.user_info import load_story, save_user_info
from utils.utils import convert_json


def get(key, default=""):
    return getattr(st.session_state, key, default)


def set(key, value, define=True):
    if not define and not hasattr(st.session_state, key):
        raise KeyError(f"st.session_state has no attribute `{key}`.")
    return setattr(st.session_state, key, value)


def wrapper(story_name: str) -> callable:
    play_info = load_story(story_name)

    def _page():
        st.title(story_name.split("_", 0)[0])

        if "chat_history" not in st.session_state:
            set("chat_history", [])
        if "is_end" not in st.session_state:
            set("is_end", False)
            # (
            #     [] if len(play_info["chat_history"]) > 0 else play_info["chat_history"][-1]
            # )

        if len(get("chat_history")) == 0:
            # res = convert_json(
            #     storyteller.init_new_session(
            #         {
            #             "worldview": play_info["worldview"],
            #             "event_history": play_info["event_history"],
            #             "user_info": play_info["user_info"],
            #         }
            #     )
            # )
            # msg = res["context"] + "\n\n<행동 예시>"
            # for i, action in enumerate(res["example_actions"]):
            #     msg += f"\n{i + 1}. {action}"
            # set("res", res)
            msg = "시작 테스트"
            st.session_state.chat_history.append({"role": "ai", "message": msg})

        for content in st.session_state.chat_history:
            with st.chat_message(content["role"]):
                st.markdown(content["message"])

        col1, col2 = st.columns([9, 1])
        with col1:
            inputs = st.chat_input("메시지를 입력하세요.", disabled=get("is_end"))

            if prompt := inputs:
                with st.chat_message("user"):
                    st.markdown(prompt)
                    st.session_state.chat_history.append({"role": "user", "message": prompt})

                # res = convert_json(storyteller.get_answer(prompt))
                # set('is_end', res["is_end"])
                # msg = res["context"]
                # if not res["is_end"]:
                #     msg += "\n\n<행동 예시>"
                #     for i, action in enumerate(res["example_actions"]):
                #         msg += f"\n{i + 1}. {action}"

                msg = "채팅 테스트: |" + prompt + "|"

                with st.chat_message("ai"):
                    st.markdown(msg)
                    st.session_state.chat_history.append({"role": "ai", "message": msg})

        with col2:
            st.button("test")

    return _page
