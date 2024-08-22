import os
import yaml
import streamlit as st

from subpages.login import Authenticate

from config import path

from story_info import StoryInfoManager

from subpages.story_view import wrapper


# Loading config file
with open(path.auth_config_dir, "r", encoding="utf-8") as file:
    config = yaml.load(file, Loader=yaml.loader.SafeLoader)

authenticator = Authenticate(**config)

# TODO: authentication_status 열거형으로 변경
if st.session_state["authentication_status"]:
    authenticator.logout(location="sidebar")

    pages = {
        "⚙️책장 관리": [
            st.Page(
                "./subpages/new_story.py",
                title="새 이야기 만들기",
                url_path="new_story",
                icon="📝",
            ),
            st.Page(
                "./subpages/manage_story.py",
                title="이야기 관리하기",
                url_path="manage_story",
                icon="📊",
            ),
        ],
        "📚이야기들": [
            st.Page(wrapper(story_name), title=story_name, url_path=f"story_{i}")
            for i, story_name in enumerate(
                StoryInfoManager.get_story_list(st.session_state["username"])
            )
        ],
    }

    nav = st.navigation(pages)
    nav.run()

else:
    st.title("가제: 인터랙티브 픽션")  # TODO: 제목 뭐하지

    st.write("내가 원하는 세계관을 직접 작성하고, 그 세계에서 자유롭게 모험을 떠나세요.")
    st.write("무슨 일이 일어날 지는 아무도 모릅니다.")
    st.write("당신은 누구인가요?")

    login_tab, registration_tab = st.tabs(["로그인", "회원가입"])

    with login_tab:
        # Creating a login widget
        try:
            authenticator.login()
            if st.session_state["authentication_status"] is False:
                st.error("사용자 이름/비밀번호가 올바르지 않습니다.")

            elif st.session_state["authentication_status"] is None:
                st.warning("사용자 아이디와 비밀번호를 입력하세요.")
        except Exception as e:
            # except LoginError as e:
            st.error(e)

    with registration_tab:
        # 회원가입
        try:
            username = authenticator.register_user()
            if username:
                os.makedirs(os.path.join(path.play_info_dir, username), exist_ok=True)
                st.success("사용자 등록 성공")
        except Exception as e:
            # except RegisterError as e:
            st.error(e)

# Saving config file
with open(path.auth_config_dir, "w", encoding="utf-8") as file:
    yaml.dump(config, file, default_flow_style=False)
