from glob import glob

import streamlit as st

from utils import load_json
from subpages.story_view import wrapper


def main():
    pages = {
        "새 이야기 시작하기": [
            st.Page("./subpages/new_story.py", title="새 이야기 만들기", icon="🔥"),
        ],
        "이어서 이야기 읽기": [
            st.Page(wrapper(load_json(fn)), title=fn, url_path=f"story_{i}")
            for i, fn in enumerate(glob("../chat_info_test/*.json"))
        ],
    }

    nav = st.navigation(pages)
    nav.run()


if __name__ == "__main__":
    main()
