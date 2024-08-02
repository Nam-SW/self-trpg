import streamlit as st


from agents.storyteller import storyteller
from agents.story_closer import story_closer
from agents.summarizer import summarizer
from agents.settlement_manager import settlement_manager

from utils.user_info import load_story, save_user_info
from utils.utils import convert_json, try_n


def get(key, default=""):
    return getattr(st.session_state, key, default)


def set(key, value, define=True):
    if not define and not hasattr(st.session_state, key):
        raise KeyError(f"st.session_state has no attribute `{key}`.")
    return setattr(st.session_state, key, value)


def send_in_scope(role, msg):
    with st.chat_message(role):
        st.markdown(msg)


def wrapper(story_name: str) -> callable:
    play_info = load_story(story_name)

    def _page():
        if "play_info" not in st.session_state:
            set("play_info", play_info)
        if "chat_history" not in st.session_state:  # chat history
            set("chat_history", [])
        if "is_end" not in st.session_state:  # event end
            set("is_end", False)
        if len(get("chat_history")) == 0:  # event initial
            res = convert_json(
                try_n(
                    storyteller.init_new_session,
                    args=[
                        {
                            "worldview": get("play_info")["worldview"],
                            "event_history": get("play_info")["event_history"],
                            "user_info": get("play_info")["user_info"],
                        }
                    ],
                )
            )
            msg = res["context"] + "\n\n<행동 예시>"
            for i, action in enumerate(res["example_actions"]):
                msg += f"\n{i + 1}. {action}"
            # set("res", res)
            # msg = f"시작 테스트 {get('play_info')['user_info']['max_hp']}"
            st.session_state.chat_history.append({"role": "ai", "message": msg})

        st.title(story_name.split("_", 0)[0])

        tab_chat, tab_event_history, tab_user_info, tab_worldview = st.tabs(
            ["모험 진행하기", "사건 로그", "유저 정보", "세계관"]
        )

        inputs = st.chat_input("텍스트를 입력하세요.")

        # 메인 채팅 뷰
        with tab_chat:
            for content in st.session_state.chat_history:
                send_in_scope(content["role"], content["message"])

            if prompt := inputs:
                if get("is_end"):
                    set("is_end", False)
                else:
                    send_in_scope("user", prompt)
                    st.session_state.chat_history.append({"role": "user", "message": prompt})

                    res = try_n(lambda: convert_json(storyteller.get_answer(prompt)))
                    set("is_end", res["is_end"])
                    msg = res["context"]
                    if not res["is_end"]:
                        msg += "\n\n<행동 예시>"
                        if isinstance(res.get("example_actions"), list):
                            for i, action in enumerate(res["example_actions"]):
                                msg += f"\n{i + 1}. {action}"
                    # if prompt == "end":
                    #     set("is_end", True)

                    # msg = "채팅 테스트: |" + prompt + "|"

                    send_in_scope("ai", msg)
                    st.session_state.chat_history.append({"role": "ai", "message": msg})

            if get("is_end"):
                # with st.chat_message("ai"):
                #     st.markdown("하나")
                # get("play_info")["event_history"].append("test")
                # get("play_info")["user_info"]["max_hp"] += 99999
                # set("chat_history", [])

                get("play_info")["chat_history"].append(storyteller.chat_history)

                # 요약
                summary = convert_json(
                    summarizer.invoke({"story_context": get("play_info")["chat_history"]})
                )
                get("play_info")["event_history"].append(summary["summary"])
                send_in_scope("ai", "사건 정리: " + summary["summary"])
                st.session_state.chat_history.append({"role": "ai", "message": msg})

                # 정산
                reward = settlement_manager.invoke(
                    {
                        "user_info": get("play_info")["user_info"],
                        "story_context": storyteller.chat_history,
                    }
                )
                reward = convert_json(reward)
                # 최대 체력 등 먼저 처리해야하는 값들
                for key in ["max_hp", "max_mental"]:
                    if key in reward:
                        get("play_info")["user_info"][key] = reward.pop(key)
                # 체력 등 상한선이 정해진 값들
                for key in ["hp", "mental"]:
                    if key in reward:
                        get("play_info")["user_info"][key] = min(
                            reward.pop(key), get("play_info")["user_info"][f"max_{key}"]
                        )
                # 나머지 단순 지정
                for key, value in reward.items():
                    if key in get("play_info")["user_info"]:
                        get("play_info")["user_info"][key] = value
                if get("play_info")["user_info"]["mental"] <= 0:
                    get("play_info")["user_info"]["characteristics"].append("미쳐버림")

                if (
                    len(get("play_info")["event_history"]) >= 5
                    or get("play_info")["user_info"]["hp"] <= 0
                ):
                    with st.chat_message("ai"):
                        st.write_stream(
                            story_closer.stream(
                                {
                                    "story_context": get("play_info")["event_history"],
                                    "last_event": storyteller.chat_history,
                                    "is_old": len(get("play_info")["event_history"]) >= 5,
                                }
                            )
                        )

                save_user_info(get("play_info"), story_name)
                set("chat_history", [])

                send_in_scope("ai", "아무 키나 입력하세요")

        # 사건 로그
        with tab_event_history:
            for content in get("play_info")["event_history"]:
                send_in_scope("user", content)

        # 유저 정보
        with tab_user_info:
            st.write(
                f"체력: {get('play_info')['user_info']['hp']} / "
                f"{get('play_info')['user_info']['max_hp']}"
            )
            st.write(
                f"정신력: {get('play_info')['user_info']['mental']} / "
                f"{get('play_info')['user_info']['max_mental']}"
            )
            st.write(f"성별: {get('play_info')['user_info']['sex']}")
            st.write(f"지위: {get('play_info')['user_info']['role']}")
            st.write(f"현재 위치: {get('play_info')['user_info']['location']}")
            st.markdown(
                f"보유 특성: `{'`, `'.join(get('play_info')['user_info']['characteristics'])}`"
            )
            st.markdown(f"보유 기술: `{'`, `'.join(get('play_info')['user_info']['skills'])}`")
            st.markdown(f"보유 아이템: `{'`, `'.join(get('play_info')['user_info']['inventory'])}`")
            st.markdown(
                f"동료: `{'`, `'.join([c['name'] for c in get('play_info')['user_info']['companion']])}`"
            )

        with tab_worldview:
            st.markdown(get("play_info")["worldview"])

    return _page
