from typing import Optional

import streamlit as st

from streamlit_authenticator import params
from streamlit_authenticator.utilities import (
    Hasher,
    LoginError,
    RegisterError,
    Validator,
)


class AuthenticationManager:
    def __init__(
        self,
        user_dict: dict,
        public_key: str,
        auto_hash: bool = True,
    ):
        self.user_dict = user_dict
        if self.user_dict:
            if "AuthenticationService.__init__" not in st.session_state:
                st.session_state["AuthenticationService.__init__"] = None
            if not st.session_state["AuthenticationService.__init__"]:
                self.user_dict = {key.lower(): value for key, value in self.user_dict.items()}
                if auto_hash:
                    if len(self.user_dict) > params.AUTO_HASH_MAX_USERS:
                        print(
                            f"""Auto hashing in progress. To avoid runtime delays, please manually
                              pre-hash all plain text passwords in the credentials using the
                              Hasher.hash_passwords function, and set auto_hash=False for the
                              Authenticate class. For more information please refer to
                              {params.AUTO_HASH_MAX_USERS_LINK}."""
                        )
                    for username, _ in self.user_dict.items():
                        if not Hasher._is_hash(self.user_dict[username]["password"]):
                            self.user_dict[username]["password"] = Hasher._hash(
                                self.user_dict[username]["password"]
                            )
                st.session_state["AuthenticationService.__init__"] = True
        else:
            self.user_dict = {}

        self.public_key = public_key
        self.validator = Validator()

        if "authentication_status" not in st.session_state:
            st.session_state["authentication_status"] = None
        if "username" not in st.session_state:
            st.session_state["username"] = None
        if "logout" not in st.session_state:
            st.session_state["logout"] = None

    def _check_public_key(self, public_key: str) -> bool:
        return self.public_key == public_key

    def _record_failed_login_attempts(self, username: str, reset: bool = False):
        """로그인 실패시 기록

        Args:
            username (str): username (id)
            reset (bool, optional): Defaults to False.
                True: 실패기록이 쌓이지 않고, 0으로 초기화됨
                False: 실패기록이 쌓임
        """
        if "failed_login_attempts" not in self.user_dict[username] or reset:
            self.user_dict[username]["failed_login_attempts"] = 0
        else:
            self.user_dict[username]["failed_login_attempts"] += 1

    def _count_concurrent_users(self) -> int:
        """현재 로그인한 유저 수 반환

        Returns:
            int: 현재 로그인한 유저 수
        """
        concurrent_users = sum(
            int(info.get("logged_in", False)) for info in self.user_dict.values()
        )
        return concurrent_users

    def check_credentials(
        self,
        username: str,
        password: str,
        public_key: str,
        max_concurrent_users: Optional[int] = None,
        max_login_attempts: Optional[int] = None,
    ) -> bool:
        if (
            isinstance(max_concurrent_users, int)
            and self._count_concurrent_users() > max_concurrent_users - 1
        ):
            raise LoginError("최대 동시접속자 수를 초과했습니다")

        if username not in self.user_dict:
            return False

        if not self._check_public_key(public_key):
            raise LoginError("올바른 퍼블릭 키를 입력하세요.")

        if (
            isinstance(max_login_attempts, int)
            and "failed_login_attempts" in self.user_dict[username]
            and self.user_dict[username]["failed_login_attempts"] >= max_login_attempts
        ):
            raise LoginError("최대 로그인 시도 횟수를 초과했습니다.")

        try:
            if Hasher.check_pw(password, self.user_dict[username]["password"]):
                return True
            self._record_failed_login_attempts(username)
            return False
        except (TypeError, ValueError) as e:
            print(e)
        return None

    def login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        public_key: Optional[str] = None,
        max_concurrent_users: Optional[int] = None,
        max_login_attempts: Optional[int] = None,
        token: Optional[dict[str, str]] = None,
    ) -> bool:
        if username:
            if self.check_credentials(
                username, password, public_key, max_concurrent_users, max_login_attempts
            ):
                st.session_state["username"] = username
                st.session_state["authentication_status"] = True
                self._record_failed_login_attempts(username, reset=True)
                self.user_dict[username]["logged_in"] = True
                return True
            st.session_state["authentication_status"] = False
            return False
        if token:
            if not token["username"] in self.user_dict:
                raise LoginError("가입하지 않은 아이디입니다.")
            st.session_state["username"] = token["username"]
            st.session_state["authentication_status"] = True
            self.user_dict[token["username"]]["logged_in"] = True
        return None

    def logout(self):
        self.user_dict[st.session_state["username"]]["logged_in"] = False
        st.session_state["logout"] = True
        st.session_state["username"] = None
        st.session_state["authentication_status"] = None

    def register_user(
        self,
        username: str,
        password: str,
        password_check: str,
        public_key: str,
    ) -> bool:
        if not self.validator.validate_username(username):
            raise RegisterError("올바르지 않은 아이디입니다.")
        if not self.validator.validate_length(password, 1) or not self.validator.validate_length(
            password_check, 1
        ):
            raise RegisterError("PW / PW check 필드를 입력하세요.")
        if password != password_check:
            raise RegisterError("동일한 비밀번호를 입력하세요.")
        # if not self.validator.validate_password(password):
        #     raise RegisterError("올바르지 않은 비밀번호입니다.")
        if not self._check_public_key(public_key):
            raise LoginError("올바른 퍼블릭 키를 입력하세요.")
        if username in self.user_dict:
            raise RegisterError("이미 가입한 아이디입니다.")

        self.user_dict[username] = {
            "username": username,
            "password": Hasher([password]).generate()[0],
            "logged_in": False,
        }
        return username
