import os
import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# from streamlit_authenticator.utilities import (
#     # CredentialsError,
#     ForgotError,
#     # Hasher,
#     LoginError,
#     RegisterError,
#     # ResetError,
#     # UpdateError,
# )

from config import path
from utils.user_info import get_story_list
from subpages.story_view import wrapper


# Loading config file
with open("../config/auth_config.yaml", "r", encoding="utf-8") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Hashing all plain text passwords once
# Hasher.hash_passwords(config['credentials'])
# Creating the authenticator object
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["pre_authorized"],
)

if st.session_state["authentication_status"]:
    authenticator.logout()

    pages = {
        "새 이야기 시작하기": [  # TODO: 페이지 관리 섹션으로 컨셉 변경?
            st.Page("./subpages/new_story.py", title="새 이야기 만들기", icon="🔥"),
            # TODO: 이야기 삭제할 수 있도록?
        ],
        "이어서 이야기 읽기": [
            st.Page(wrapper(story_name), title=story_name, url_path=f"story_{i}")
            for i, story_name in enumerate(get_story_list(st.session_state["username"]))
        ],
    }

    nav = st.navigation(pages)
    nav.run()

else:
    login_tab, registration_tab, find_id_tab, find_pw_tab = st.tabs(
        ["로그인", "회원가입", "아이디 찾기", "비밀번호 찾기"]
    )

    with login_tab:
        # Creating a login widget
        try:
            authenticator.login(
                fields={
                    "Form name": "로그인",
                    "Username": "아이디",
                    "Password": "비밀번호",
                    "Login": "로그인",
                }
            )
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
            (email, user_id, name) = authenticator.register_user(
                fields={
                    "Form name": "회원가입",
                    "Name": "닉네임",
                    "Email": "이메일",
                    "Username": "아이디",
                    "Password": "비밀번호",
                    "Repeat password": "비밀번호 확인",
                    "Register": "등록",
                },
                pre_authorization=False,
                # captcha=False,
            )
            # print(email, user_id, name)
            if email:
                os.makedirs(os.path.join(path.story_dir, user_id))
                st.success("사용자 등록 성공")
        except Exception as e:
            # except RegisterError as e:
            st.error(e)

    with find_id_tab:
        # 아이디 찾기
        try:
            (username_of_forgotten_username, email_of_forgotten_username) = (
                authenticator.forgot_username()
            )
            if username_of_forgotten_username:
                st.success("사용자 아이디 메일로 보내기(미구현)")
            elif not username_of_forgotten_username:
                st.error("등록되지 않은 이메일입니다.")
        except Exception as e:
            # except ForgotError as e:
            st.error(e)

    with find_pw_tab:
        # 비밀번호 찾기
        try:
            (username_of_forgotten_password, email_of_forgotten_password, new_random_password) = (
                authenticator.forgot_password()
            )
            if username_of_forgotten_password:
                st.success("사용자 비밀번호 메일로 보내기(미구현)")
            elif not username_of_forgotten_password:
                st.error("등록되지 않은 이름입니다.")
        except Exception as e:
            # except ForgotError as e:
            st.error(e)


# Saving config file
with open("../config/auth_config.yaml", "w", encoding="utf-8") as file:
    yaml.dump(config, file, default_flow_style=False)
