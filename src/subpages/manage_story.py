import streamlit as st
import pandas as pd


from story_info import StoryInfoManager


if not hasattr(st.session_state, "stories"):
    st.session_state["stories"] = {
        story_name: StoryInfoManager.load(st.session_state["username"], story_name)
        for story_name in StoryInfoManager.get_story_list(st.session_state["username"])
    }


df = pd.DataFrame(
    [
        {
            "생성일자": story_name.split("_", 1)[0],
            "이야기 제목": story_name.split("_", 1)[1],
            "진행도": f"{len(info)} / {info['limit_event']}",
            "이야기 종료": (
                "O" if len(info) >= info["limit_event"] or info.get_user_info()["hp"] <= 0 else "X"
            ),
        }
        for story_name, info in st.session_state["stories"].items()
    ]
)


st.title("이야기 관리하기")
st.markdown("`삭제` 버튼을 눌러 이야기를 삭제할 수 있습니다.")
st.markdown("`초기화` 버튼을 눌러 이야기를 처음부터 다시 시작할 수 있습니다.")
st.markdown("`마지막 사건 재시작` 마지막에 진행한 사건을 다시 시작할 수 있습니다.")
st.warning("주의: 버튼 클릭시 재확인하지 않고 즉시 실행됩니다.")

stories = st.dataframe(df, hide_index=True, on_select="rerun", selection_mode="multi-row")


c1, c2, c3, c4 = st.columns(4)

with c1:
    remove_btn = st.button("삭제")
with c2:
    init_btn = st.button("초기화")
with c3:
    restart_btn = st.button("마지막 사건 재시작")
with c4:
    if st.button("새로고침", type="primary"):
        st.session_state["stories"] = {
            story_name: StoryInfoManager.load(st.session_state["username"], story_name)
            for story_name in StoryInfoManager.get_story_list(st.session_state["username"])
        }


if remove_btn:
    if len(stories.selection["rows"]) < 1:
        st.info("1개 이상의 이야기를 선택하세요.")
    else:
        keys = df.iloc[stories.selection["rows"]].apply(
            lambda row: f"{row['생성일자']}_{row['이야기 제목']}", axis=1
        )
        for key in keys:
            del st.session_state["stories"][key]
            StoryInfoManager.remove(st.session_state["username"], key)
        st.success("삭제가 완료되었습니다. 새로고침 후 좌측 사이드바를 확인하세요.")


if init_btn:
    if len(stories.selection["rows"]) < 1:
        st.info("1개 이상의 이야기를 선택하세요.")
    else:
        keys = df.iloc[stories.selection["rows"]].apply(
            lambda row: f"{row['생성일자']}_{row['이야기 제목']}", axis=1
        )
        for key in keys:  # 플레이중 초기화 할 수 있으니 새로 불러오기
            info = StoryInfoManager.load(st.session_state["username"], key)
            info.reset()
            info.save()
        st.success("초기화가 완료되었습니다. 새로고침해 확인하세요.")

if restart_btn:
    if len(stories.selection["rows"]) < 1:
        st.info("1개 이상의 이야기를 선택하세요.")
    else:
        keys = df.iloc[stories.selection["rows"]].apply(
            lambda row: f"{row['생성일자']}_{row['이야기 제목']}", axis=1
        )
        for key in keys:  # 플레이중 롤백 할 수 있으니 새로 불러오기
            info = StoryInfoManager.load(st.session_state["username"], key)
            info.rollback_to_prev_event()
            info.save()
        st.success("마지막 사건으로 롤백이 완료되었습니다. 새로고침해 확인하세요.")
