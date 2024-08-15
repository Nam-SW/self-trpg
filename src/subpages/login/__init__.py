import time
from typing import Optional
import streamlit as st

# from .. import params
from streamlit_authenticator.controllers import CookieController
from streamlit_authenticator.utilities import LoginError, LogoutError
from streamlit_authenticator.utilities.hasher import Hasher

from subpages.login.auth_manager import AuthenticationManager


class Authenticate:
    """
    This class renders login, logout, register user, reset password, forgot password,
    forgot username, and modify user details widgets.
    """

    def __init__(
        self,
        user_dict: dict,
        cookie: dict,
        public_key: str,
        auto_hash: bool = True,
    ):
        self.authentication_controller = AuthenticationManager(user_dict, public_key, auto_hash)
        self.cookie_controller = CookieController(**cookie)
        if not st.session_state["authentication_status"]:
            token = self.cookie_controller.get_cookie()
            if token:
                try:
                    self.authentication_controller.login(token=token)
                except Exception as e:
                    self.cookie_controller.delete_cookie()
                    st.write("로그인 정보가 올바르지 않습니다. 페이지를 새로고침 해주세요.")

    def login(
        self,
        location: str = "main",
        max_concurrent_users: Optional[int] = None,
        max_login_attempts: Optional[int] = None,
        clear_on_submit: bool = False,
        sleep_time: Optional[float] = None,
    ) -> tuple:
        key = "Login"

        if location not in ["main", "sidebar", "unrendered"]:
            raise ValueError("Location must be one of 'main' or 'sidebar' or 'unrendered'")
        if not st.session_state["authentication_status"]:
            token = self.cookie_controller.get_cookie()
            if token:
                self.authentication_controller.login(token=token)
            # time.sleep(0.5 if sleep_time is None else sleep_time)
            if not st.session_state["authentication_status"]:
                if location == "main":
                    login_form = st.form(key=key, clear_on_submit=clear_on_submit)
                elif location == "sidebar":
                    login_form = st.sidebar.form(key=key, clear_on_submit=clear_on_submit)
                elif location == "unrendered":
                    return (
                        st.session_state["authentication_status"],
                        st.session_state["username"],
                    )
                login_form.subheader("로그인")
                username = login_form.text_input("ID")
                password = login_form.text_input("PW", type="password")
                public_key = login_form.text_input("public key", type="password")

                if login_form.form_submit_button("로그인"):
                    if self.authentication_controller.login(
                        username,
                        password,
                        public_key,
                        max_concurrent_users,
                        max_login_attempts,
                    ):
                        self.cookie_controller.set_cookie()
        return (
            st.session_state["authentication_status"],
            st.session_state["username"],
        )

    def logout(
        self,
        button_name: str = "Logout",
        location: str = "main",
    ):
        key = "Logout"
        if not st.session_state["authentication_status"]:
            raise LogoutError("User must be logged in to use the logout button")
        if location not in ["main", "sidebar", "unrendered"]:
            raise ValueError("Location must be one of 'main' or 'sidebar' or 'unrendered'")
        if location == "main":
            if st.button(button_name, key=key):
                st.session_state["authentication_status"] = False
                self.authentication_controller.logout()
                self.cookie_controller.delete_cookie()

        elif location == "sidebar":
            if st.sidebar.button(button_name, key=key):
                st.session_state["authentication_status"] = False
                self.authentication_controller.logout()
                self.cookie_controller.delete_cookie()

        elif location == "unrendered":
            if st.session_state["authentication_status"]:
                st.session_state["authentication_status"] = False
                self.authentication_controller.logout()
                self.cookie_controller.delete_cookie()

    def register_user(
        self,
        location: str = "main",
        clear_on_submit: bool = False,
        key: str = "Register user",
    ) -> tuple:

        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            register_user_form = st.form(key=key, clear_on_submit=clear_on_submit)
        elif location == "sidebar":
            register_user_form = st.sidebar.form(key=key, clear_on_submit=clear_on_submit)

        register_user_form.subheader("회원가입")

        username = register_user_form.text_input("ID")
        password = register_user_form.text_input("PW", type="password")
        password_check = register_user_form.text_input("PW check", type="password")
        public_key = register_user_form.text_input("public key", type="password")

        if register_user_form.form_submit_button("회원가입"):
            return self.authentication_controller.register_user(
                username, password, password_check, public_key
            )
        return
