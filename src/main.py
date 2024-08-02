import streamlit as st

from utils.user_info import get_story_list
from subpages.story_view import wrapper

# from subpages.story_viewa import wrapper


def main():
    pages = {
        "새 이야기 시작하기": [  # TODO: 페이지 관리 섹션으로 컨셉 변경?
            st.Page("./subpages/new_story.py", title="새 이야기 만들기", icon="🔥"),
            # TODO: 이야기 삭제할 수 있도록?
        ],
        "이어서 이야기 읽기": [
            st.Page(wrapper(story_name), title=story_name, url_path=f"story_{i}")
            for i, story_name in enumerate(get_story_list())
            # TODO: db에서 chat_id랑 제목만 가져오게 수정? 제목 가져오려면 세계관 작성부도 수정해야함
        ],
    }

    nav = st.navigation(pages)
    nav.run()


if __name__ == "__main__":
    main()
