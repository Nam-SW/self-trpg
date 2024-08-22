import streamlit as st


from agents.screenwriter import world_to_document
from agents.storyteller import get_storyteller
from agents.story_closer import get_story_closer
from agents.summarizer import get_summarizer
from agents.settlement_manager import get_settlement_manager

from story_info import StoryInfoManager
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
    if not hasattr(st.session_state, story_name + "story_info"):
        st.session_state[story_name + "story_info"] = StoryInfoManager.load(
            st.session_state["username"], story_name
        )

    get_state("storyteller").set_system_prompt(
        {
            "worldview": world_to_document(get_state("story_info")["worldview"], True),
            "story_history": get_state("story_info").get_story_summary(),
            "event_summarized_history": (
                get_state("story_info").get_event_summarized_history(-2)
                if len(get_state("story_info")) >= 2
                else []
            ),
            "user_info": get_state("story_info").get_user_info(),
            "now_turn": len(get_state("story_info")),
            "max_turn": get_state("story_info")["limit_event"],
        }
    )
    get_state("storyteller").set_chat_history(
        summary=get_state("story_info").get_event_summarized_history(),
        detail=get_state("story_info").get_event_original_history(),
    )

    def _page():

        st.title(story_name.split("_", 1)[1].replace("_", " "))
        st.slider(
            "이야기 진행도",
            0,
            get_state("story_info")["limit_event"],
            len(get_state("story_info")),
            disabled=True,
        )
        tab_chat, tab_event_history, tab_chat_histroy, tab_user_info, tab_worldview = st.tabs(
            ["모험 진행하기", "이야기 요약", "사건별 기억", "유저 정보", "세계관"]
        )
        inputs = st.chat_input(
            "텍스트를 입력하세요.",
            disabled=get_state("story_info").is_story_end(),
        )

        if get_state("story_info").is_story_end():  # 엔딩
            # 만약 엔딩이 없다면
            if get_state("story_info")["ending"] is None:
                with st.spinner("이야기를 마무리 짓는 중..."):
                    ending = get_state("story_closer").invoke(
                        {
                            "story_context": get_state("story_info").get_story_summary(),
                            "last_event": get_state("story_info").get_event_summarized_history(),
                            "is_old": get_state("story_info").is_over_event_limit(),
                        }
                    )
                get_state("story_info").add_ending(ending)
                get_state("story_info").save()

        # 메인 채팅 뷰
        with tab_chat:
            original_history = get_state("story_info").get_event_original_history()
            init_event = len(original_history) == 0

            if get_state("story_info").is_story_end():
                send_in_scope("ai", get_state("story_info")["ending"])
            else:
                for content in original_history:
                    send_in_scope(content["role"], content["message"])

                if init_event:
                    send_in_scope("ai", "아무 값이나 입력해 시작하기")

            if (action := inputs) and not get_state("story_info").is_story_end():
                # 사건 시작: init new session
                if init_event:
                    get_state("storyteller").clear_history()
                    get_state("storyteller").set_system_prompt(
                        {
                            "worldview": world_to_document(
                                get_state("story_info")["worldview"], True
                            ),
                            "story_history": get_state("story_info").get_story_summary(),
                            "event_summarized_history": (
                                get_state("story_info").get_event_summarized_history(-2)
                                if len(get_state("story_info")) >= 2
                                else []
                            ),
                            "user_info": get_state("story_info").get_user_info(),
                            "now_turn": len(get_state("story_info")),
                            "max_turn": get_state("story_info")["limit_event"],
                        }
                    )
                    action = ""
                else:
                    send_in_scope("user", action)

                with st.spinner("작성중..."):
                    res = try_n(
                        get_state("storyteller").get_answer,
                        [
                            {
                                # "previous_chat": prev_chat,
                                "action": action,
                            }
                        ],
                    )

                origin_msg = "\n\n".join(res["detail"])
                msg = origin_msg

                if len(res["example_actions"]) and (init_event or not res["is_end"]):
                    msg += "\n\n<행동 예시>"
                    for i, ex_act in enumerate(res["example_actions"]):
                        msg += f"\n{i + 1}. {ex_act}"

                if not init_event:
                    get_state("story_info").add_original_chat("user", action)
                    get_state("story_info").add_summary_chat("user", action)
                get_state("story_info").add_original_chat("ai", origin_msg)
                get_state("story_info").add_summary_chat("ai", res["plot"])
                send_in_scope("ai", msg)

                if not init_event and res["is_end"]:  # 이야기 시작하자마자 끝나지 않도록
                    get_state("story_info").set_event_end()

                get_state("story_info").save()

            if get_state("story_info").is_event_end():
                send_in_scope("ai", "사건이 종료되었습니다.")

                # 요약
                with st.spinner("사건을 마무리하는 중..."):
                    summarize_result = get_state("summarizer").invoke(
                        {
                            "worldview": world_to_document(
                                get_state("story_info")["worldview"], True
                            ),
                            "story_context": get_state("story_info").get_event_original_history(),
                        }
                    )
                    summary = summarize_result["summary"]
                    story_end = summarize_result["story_end"]
                send_in_scope("ai", "사건 정리: " + summary)

                # 정산
                with st.spinner("사건 뒷정리 중..."):
                    user_info = get_state("settlement_manager").invoke(
                        {
                            "user_info": get_state("story_info").get_user_info(),
                            "story_context": get_state("story_info").get_event_original_history(),
                        }
                    )

                if user_info["mental"] <= 0 and "미쳐버림" not in user_info["characteristics"]:
                    user_info["characteristics"].append("미쳐버림")

                get_state("story_info").add_new_event(prev_summary=summary, **user_info)

                if story_end:
                    get_state("story_info").set_story_end()

                get_state("story_info").save()
                send_in_scope("ai", "아무 키나 입력하여 다음 사건으로 넘어가기")

        # 사건 로그
        with tab_event_history:
            for content in get_state("story_info").get_story_summary():
                send_in_scope("user", content)

        # 거시기 그 뭐냐 아무튼 그거
        with tab_chat_histroy:
            if len(get_state("story_info")) > 1:
                event_view_idx = st.slider(
                    "사건 선택",
                    min_value=min(1, len(get_state("story_info")) - 1),
                    max_value=len(get_state("story_info")) - 1,
                )
                hist = get_state("story_info").get_event_original_history(event_view_idx - 1)
                for content in hist:
                    send_in_scope(content["role"], content["message"])

            else:
                st.write("하나 이상의 사건을 마치고 난 후 기억을 되짚을 수 있습니다.")

        # 유저 정보
        with tab_user_info:
            user_info = get_state("story_info").get_user_info()
            st.write(f"체력: {user_info['hp']} / " f"{user_info['max_hp']}")
            st.write(f"정신력: {user_info['mental']} / " f"{user_info['max_mental']}")
            st.write(f"성별: {user_info['sex']}")
            st.write(f"지위: {user_info['role']}")
            st.write(f"현재 위치: {user_info['location']}")
            st.markdown(f"보유 특성: `{'`, `'.join(user_info['characteristics'])}`")
            st.markdown(f"보유 기술: `{'`, `'.join(user_info['skills'])}`")
            st.markdown(f"보유 아이템: `{'`, `'.join(user_info['inventory'])}`")
            st.markdown(f"동료: `{'`, `'.join([c['name'] for c in user_info['companion']])}`")

        with tab_worldview:
            # st.markdown(get_state("story_info")["worldview"])
            st.markdown(world_to_document(get_state("story_info")["worldview"]))

    return _page
