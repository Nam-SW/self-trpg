import streamlit as st


from agents.storyteller import get_storyteller
from agents.story_closer import get_story_closer
from agents.summarizer import get_summarizer
from agents.settlement_manager import get_settlement_manager

from utils.user_info import load_story, save_story
from utils.utils import try_n


def send_in_scope(role, msg):
    with st.chat_message(role):
        st.markdown(msg)


def wrapper(story_name: str) -> callable:
    def get_state(key):
        return getattr(st.session_state, story_name + key)

    if not hasattr(st.session_state, story_name + "storyteller"):
        st.session_state[story_name + "storyteller"] = get_storyteller()
    if not hasattr(st.session_state, story_name + "story_closer"):
        st.session_state[story_name + "story_closer"] = get_story_closer()
    if not hasattr(st.session_state, story_name + "summarizer"):
        st.session_state[story_name + "summarizer"] = get_summarizer()
    if not hasattr(st.session_state, story_name + "settlement_manager"):
        st.session_state[story_name + "settlement_manager"] = get_settlement_manager()
    if not hasattr(st.session_state, story_name + "play_info"):
        st.session_state[story_name + "play_info"] = load_story(
            st.session_state["username"], story_name
        )

    get_state("storyteller").set_system_prompt(
        {
            "worldview": get_state("play_info")["worldview"],
            "event_history": get_state("play_info")["event_history"],
            "user_info": get_state("play_info")["user_info"],
            "last_chat": (
                get_state("play_info")["chat_summary_history"][-2]
                if len(get_state("play_info")["chat_summary_history"]) >= 2
                else []
            ),
        }
    )
    get_state("storyteller").chat_history = get_state("play_info")["chat_summary_history"][-1]

    def _page():
        over_event_limit = (
            len(get_state("play_info")["event_history"]) >= get_state("play_info")["limit_event"]
        )
        is_end = over_event_limit or get_state("play_info")["user_info"]["hp"] <= 0

        st.title(story_name.split("_", 1)[1].replace("_", " "))
        st.slider(
            "이야기 진행도",
            0,
            get_state("play_info")["limit_event"],
            len(get_state("play_info")["event_history"]),
            disabled=True,
        )
        tab_chat, tab_event_history, tab_user_info, tab_worldview = st.tabs(
            ["모험 진행하기", "사건 로그", "유저 정보", "세계관"]
        )
        inputs = st.chat_input(
            "텍스트를 입력하세요.",
            disabled=is_end,
        )

        if is_end:  # 엔딩
            # 만약 엔딩이 없다면
            if len(get_state("play_info")["chat_summary_history"][-1]) == 0:
                ending = get_state("story_closer").invoke(
                    {
                        "story_context": get_state("play_info")["event_history"],
                        "last_event": get_state("play_info")["chat_summary_history"][-1],
                        "is_old": over_event_limit,
                    }
                )
                get_state("play_info")["chat_summary_history"][-1].append(
                    {"role": "ai", "message": ending}
                )
                save_story(st.session_state["username"], get_state("play_info"), story_name)

        # 메인 채팅 뷰
        with tab_chat:
            if len(get_state("play_info")["chat_view_history"][-1]) == 0:
                send_in_scope("ai", "아무 값이나 입력해 시작하기")

            for content in get_state("play_info")["chat_view_history"][-1]:
                if content is not None:
                    send_in_scope(content["role"], content["message"])

            if prompt := inputs:
                if is_end:
                    pass

                # 사건 시작: init new session
                elif len(get_state("play_info")["chat_summary_history"][-1]) == 0:
                    get_state("storyteller").set_system_prompt(
                        {
                            "worldview": get_state("play_info")["worldview"],
                            "event_history": get_state("play_info")["event_history"],
                            "user_info": get_state("play_info")["user_info"],
                            "last_chat": (
                                get_state("play_info")["chat_summary_history"][-2]
                                if len(get_state("play_info")["chat_summary_history"]) >= 2
                                else []
                            ),
                        }
                    )
                    res = try_n(get_state("storyteller").init_new_session)
                    msg = "\n\n".join(res["detail"])
                    if res["example_actions"] is not None and len(res["example_actions"]):
                        msg += "\n\n<행동 예시>"
                        for i, action in enumerate(res["example_actions"]):
                            msg += f"\n{i + 1}. {action}"

                    send_in_scope("ai", msg)
                    get_state("play_info")["chat_summary_history"][-1] = get_state(
                        "storyteller"
                    ).chat_history
                    get_state("play_info")["chat_view_history"][-1].append(
                        {"role": "ai", "message": "\n\n".join(res["detail"])}
                    )
                    save_story(st.session_state["username"], get_state("play_info"), story_name)

                # 그냥 채팅
                else:
                    send_in_scope("user", prompt)

                    res = try_n(get_state("storyteller").get_answer, [prompt])
                    msg = "\n\n".join(res["detail"])
                    if (
                        not res["is_end"]
                        and res["example_actions"] is not None
                        and len(res["example_actions"])
                    ):
                        msg += "\n\n<행동 예시>"
                        for i, action in enumerate(res["example_actions"]):
                            msg += f"\n{i + 1}. {action}"

                    send_in_scope("ai", msg)
                    get_state("play_info")["chat_summary_history"][-1] = get_state(
                        "storyteller"
                    ).chat_history
                    get_state("play_info")["chat_view_history"][-1] += [
                        {"role": "user", "message": prompt},
                        {"role": "ai", "message": "\n\n".join(res["detail"])},
                    ]
                    if res["is_end"]:
                        get_state("play_info")["chat_summary_history"][-1].append(None)
                    save_story(st.session_state["username"], get_state("play_info"), story_name)

            if (
                len(get_state("play_info")["chat_summary_history"][-1]) > 0
                and get_state("play_info")["chat_summary_history"][-1][-1] is None
            ):
                send_in_scope("ai", "사건이 종료되었습니다.")

                get_state("play_info")["chat_summary_history"].append([])
                get_state("play_info")["chat_view_history"].append([])

                # 요약
                summary = get_state("summarizer").invoke(
                    {"story_context": get_state("storyteller").chat_history}
                )
                send_in_scope("ai", "사건 정리: " + summary)
                get_state("play_info")["event_history"].append(summary)

                # 정산
                reward = get_state("settlement_manager").invoke(
                    {
                        "user_info": get_state("play_info")["user_info"],
                        "story_context": get_state("storyteller").chat_history,
                    }
                )
                # 최대 체력 등 먼저 처리해야하는 값들
                for key in ["max_hp", "max_mental"]:
                    if key in reward:
                        get_state("play_info")["user_info"][key] = reward.pop(key)
                # 체력 등 상한선이 정해진 값들
                for key in ["hp", "mental"]:
                    if key in reward:
                        get_state("play_info")["user_info"][key] = min(
                            reward.pop(key), get_state("play_info")["user_info"][f"max_{key}"]
                        )
                # 나머지 단순 지정
                for key, value in reward.items():
                    if key in get_state("play_info")["user_info"]:
                        get_state("play_info")["user_info"][key] = value
                if (
                    get_state("play_info")["user_info"]["mental"] <= 0
                    and "미쳐버림" not in get_state("play_info")["user_info"]["characteristics"]
                ):
                    get_state("play_info")["user_info"]["characteristics"].append("미쳐버림")

                save_story(st.session_state["username"], get_state("play_info"), story_name)

                send_in_scope("ai", "아무 키나 입력하여 다음 사건으로 넘어가기")

        # 사건 로그
        with tab_event_history:
            for content in get_state("play_info")["event_history"]:
                send_in_scope("user", content)

        # 유저 정보
        with tab_user_info:
            st.write(
                f"체력: {get_state('play_info')['user_info']['hp']} / "
                f"{get_state('play_info')['user_info']['max_hp']}"
            )
            st.write(
                f"정신력: {get_state('play_info')['user_info']['mental']} / "
                f"{get_state('play_info')['user_info']['max_mental']}"
            )
            st.write(f"성별: {get_state('play_info')['user_info']['sex']}")
            st.write(f"지위: {get_state('play_info')['user_info']['role']}")
            st.write(f"현재 위치: {get_state('play_info')['user_info']['location']}")
            st.markdown(
                f"보유 특성: `{'`, `'.join(get_state('play_info')['user_info']['characteristics'])}`"
            )
            st.markdown(
                f"보유 기술: `{'`, `'.join(get_state('play_info')['user_info']['skills'])}`"
            )
            st.markdown(
                f"보유 아이템: `{'`, `'.join(get_state('play_info')['user_info']['inventory'])}`"
            )
            st.markdown(
                f"동료: `{'`, `'.join([c['name'] for c in get_state('play_info')['user_info']['companion']])}`"
            )

        with tab_worldview:
            st.markdown(get_state("play_info")["worldview"])

    return _page
