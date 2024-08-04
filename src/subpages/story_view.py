import streamlit as st


from agents.storyteller import storyteller
from agents.story_closer import story_closer
from agents.summarizer import summarizer
from agents.settlement_manager import settlement_manager

from utils.user_info import load_story, save_user_info
from utils.utils import convert_json, try_n


# def get(key, default=""):
#     return getattr(st.session_state, key, default)


# def set(key, value, define=True):
#     if not define and not hasattr(st.session_state, key):
#         raise KeyError(f"st.session_state has no attribute `{key}`.")
#     return setattr(st.session_state, key, value)


def send_in_scope(role, msg):
    with st.chat_message(role):
        st.markdown(msg)


def wrapper(story_name: str) -> callable:
    play_info = load_story(story_name)
    storyteller.set_system_prompt(
        {
            "worldview": play_info["worldview"],
            "event_history": play_info["event_history"],
            "user_info": play_info["user_info"],
        }
    )
    storyteller.chat_history = play_info["chat_history"][-1]
    # set("play_info", play_info)

    def _page():
        over_event_limit = len(play_info["event_history"]) >= play_info["limit_event"]

        st.title(story_name.split("_", 0)[0])
        st.slider(
            "이야기 진행도",
            0,
            play_info["limit_event"],
            len(play_info["event_history"]),
            disabled=True,
        )
        tab_chat, tab_event_history, tab_user_info, tab_worldview = st.tabs(
            ["모험 진행하기", "사건 로그", "유저 정보", "세계관"]
        )
        inputs = st.chat_input(
            "텍스트를 입력하세요.",
            disabled=over_event_limit,
        )

        if over_event_limit or play_info["user_info"]["hp"] <= 0:  # 엔딩
            # 만약 엔딩이 기록되어있으면
            # if len(play_info["event_history"]) != len(play_info["chat_history"]):
            if len(play_info["chat_history"][-1]) == 0:
                ending = story_closer.invoke(
                    {
                        "story_context": play_info["event_history"],
                        "last_event": play_info["chat_history"][-1],
                        "is_old": over_event_limit,
                    }
                )
                play_info["chat_history"][-1].append({"role": "ai", "message": ending})
                save_user_info(play_info, story_name)

        # 메인 채팅 뷰
        with tab_chat:
            if len(play_info["chat_history"][-1]) == 0:
                send_in_scope("ai", "아무 값이나 입력해 시작하기")

            for content in play_info["chat_history"][-1]:
                if content is not None:
                    send_in_scope(content["role"], content["message"])

            if prompt := inputs:
                # 사건 시작: init new session
                if len(play_info["chat_history"][-1]) == 0:
                    storyteller.set_system_prompt(
                        {
                            "worldview": play_info["worldview"],
                            "event_history": play_info["event_history"],
                            "user_info": play_info["user_info"],
                        }
                    )
                    res = convert_json(try_n(storyteller.init_new_session))
                    msg = res["context"] + "\n\n<행동 예시>"
                    for i, action in enumerate(res["example_actions"]):
                        msg += f"\n{i + 1}. {action}"

                    send_in_scope("ai", msg)
                    play_info["chat_history"][-1] = storyteller.chat_history
                    save_user_info(play_info, story_name)

                # # 사건 종료:
                # elif play_info["chat_history"][-1][-1] is None:
                #     set("chat_sess", [])

                # 그냥 채팅
                else:
                    send_in_scope("user", prompt)

                    res = try_n(lambda: convert_json(storyteller.get_answer(prompt)))
                    msg = res["context"]
                    if not res["is_end"]:
                        msg += "\n\n<행동 예시>"
                        if isinstance(res.get("example_actions"), list):
                            for i, action in enumerate(res["example_actions"]):
                                msg += f"\n{i + 1}. {action}"

                    send_in_scope("ai", msg)
                    play_info["chat_history"][-1] = storyteller.chat_history
                    if res["is_end"]:
                        play_info["chat_history"][-1].append(None)
                    save_user_info(play_info, story_name)

            if len(play_info["chat_history"][-1]) > 0 and play_info["chat_history"][-1][-1] is None:
                send_in_scope("ai", "사건이 종료되었습니다.")
                # with st.chat_message("ai"):
                #     st.markdown("하나")
                # play_info["event_history"].append("test")
                # play_info["user_info"]["max_hp"] += 99999
                # set("chat_history", [])

                # if len(play_info["chat_history"]) == len(play_info["event_history"])
                play_info["chat_history"].append([])
                # play_info["chat_history"].append(storyteller.chat_history)

                # 요약
                summary = convert_json(
                    summarizer.invoke({"story_context": storyteller.chat_history})
                )
                send_in_scope("ai", "사건 정리: " + summary["summary"])
                play_info["event_history"].append(summary["summary"])

                # 정산
                reward = settlement_manager.invoke(
                    {
                        "user_info": play_info["user_info"],
                        "story_context": storyteller.chat_history,
                    }
                )
                reward = convert_json(reward)
                # 최대 체력 등 먼저 처리해야하는 값들
                for key in ["max_hp", "max_mental"]:
                    if key in reward:
                        play_info["user_info"][key] = reward.pop(key)
                # 체력 등 상한선이 정해진 값들
                for key in ["hp", "mental"]:
                    if key in reward:
                        play_info["user_info"][key] = min(
                            reward.pop(key), play_info["user_info"][f"max_{key}"]
                        )
                # 나머지 단순 지정
                for key, value in reward.items():
                    if key in play_info["user_info"]:
                        play_info["user_info"][key] = value
                if play_info["user_info"]["mental"] <= 0:
                    play_info["user_info"]["characteristics"].append("미쳐버림")

                save_user_info(play_info, story_name)

                send_in_scope("ai", "아무 키나 입력하여 다음 사건으로 넘어가기")

        # 사건 로그
        with tab_event_history:
            for content in play_info["event_history"]:
                send_in_scope("user", content)

        # 유저 정보
        with tab_user_info:
            st.write(
                f"체력: {play_info['user_info']['hp']} / " f"{play_info['user_info']['max_hp']}"
            )
            st.write(
                f"정신력: {play_info['user_info']['mental']} / "
                f"{play_info['user_info']['max_mental']}"
            )
            st.write(f"성별: {play_info['user_info']['sex']}")
            st.write(f"지위: {play_info['user_info']['role']}")
            st.write(f"현재 위치: {play_info['user_info']['location']}")
            st.markdown(f"보유 특성: `{'`, `'.join(play_info['user_info']['characteristics'])}`")
            st.markdown(f"보유 기술: `{'`, `'.join(play_info['user_info']['skills'])}`")
            st.markdown(f"보유 아이템: `{'`, `'.join(play_info['user_info']['inventory'])}`")
            st.markdown(
                f"동료: `{'`, `'.join([c['name'] for c in play_info['user_info']['companion']])}`"
            )

        with tab_worldview:
            st.markdown(play_info["worldview"])

    return _page
