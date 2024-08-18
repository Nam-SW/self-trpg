import os
import re
import datetime as dt
from typing import Any, Optional

from utils.file_io import dump_json, load_json
from config import path
from .data import Chat, EventInfo, StoryInfo, UserInfo


class StoryInfoManager:
    # magic function
    def __init__(
        self,
        username: str,
        story_name: str,
        info: Optional[StoryInfo] = None,
        main_theme: Optional[str] = None,
        keywords: Optional[str] = None,
        worldview: Optional[str] = None,
        prev_summary: Optional[str] = None,
        role: Optional[str] = None,
        sex: Optional[str] = None,
        location: Optional[str] = None,
        **kwargs
    ) -> None:
        self.username = username
        if story_name == "":
            if main_theme is not None:
                story_name = main_theme
            else:
                story_name = "이야기"
        self.story_name = story_name.replace(" ", "_")
        if re.match(r"\d{12}_.+", self.story_name) is None:
            self.story_name = dt.datetime.now().strftime("%y%m%d%H%M%S_") + self.story_name

        if info is not None:
            self.info = info
            # if isinstance(info, StoryInfo):  # 이거 체크
            #     self.info = info
            # else:
            #     raise TypeError("type of `info` must be StoryInfo.")

        else:
            self.info = StoryInfo(
                main_theme=main_theme,
                keywords=keywords,
                worldview=worldview,
                limit_event=kwargs.get("limit_event", 50),
                events=[],
                ending=None,
            )
            self.add_new_event(prev_summary, role, sex, location, **kwargs)

    def __getitem__(self, key: str) -> Any:
        return self.info[key]

    def __len__(self) -> int:
        return len(self.info["events"])

    # get
    def get_story_name(self) -> str:
        return self.story_name.split("_", 1)[1].replace("_", " ")

    def get_story_summary(self) -> list[str]:
        return [event["prev_summary"] for event in self.info["events"]]

    def get_event_original_history(self, idx: int = -1) -> list[Chat]:
        return self.info["events"][idx]["original_history"]

    def get_event_summarized_history(self, idx: int = -1) -> list[Chat]:
        return self.info["events"][idx]["summarized_history"]

    def get_user_info(self, idx: int = -1) -> UserInfo:
        return self.info["events"][idx]["user_info"]

    # condition
    def is_event_end(self) -> bool:
        return self.info["events"][-1]["is_end"]

    def is_over_event_limit(self) -> bool:
        return len(self) >= self.info["limit_event"]

    def is_story_end(self) -> bool:
        return self.is_over_event_limit() or self.get_user_info()["hp"] <= 0

    # set data
    def set_event_end(self):
        self.info["events"][-1]["is_end"] = True

    def add_original_chat(self, role: str, context: str):
        self.info["events"][-1]["original_history"].append({"role": role, "message": context})

    def add_summary_chat(self, role: str, context: str):
        self.info["events"][-1]["summarized_history"].append({"role": role, "message": context})

    def add_ending(self, ending: str):
        self.info["ending"] = ending

    def add_new_event(self, prev_summary: str, role: str, sex: str, location: str, **kwargs):
        self.info["events"].append(
            EventInfo(
                summarized_history=kwargs.get("summarized_history", []),
                original_history=kwargs.get("original_history", []),
                prev_summary=prev_summary,
                user_info=UserInfo(
                    role=role,
                    sex=sex,
                    location=location,
                    hp=kwargs.get("hp", 100),
                    mental=kwargs.get("mental", 100),
                    max_hp=kwargs.get("max_hp", 100),
                    max_mental=kwargs.get("max_mental", 100),
                    characteristics=kwargs.get("characteristics", []),
                    skills=kwargs.get("skills", []),
                    inventory=kwargs.get("inventory", []),
                    companion=kwargs.get("companion", []),
                ),
                is_end=False,
            )
        )

    # remove data
    def reset(self):
        self.info["events"] = self.info["events"][:1]
        self.info["events"][0]["original_history"] = []
        self.info["events"][0]["summarized_history"] = []
        self.info["events"][0]["is_end"] = False
        self.info["ending"] = None

    def rollback_to_prev_event(self):
        if len(self) > 1 and len(self.get_event_original_history(-1)) <= 1:
            # 이제 단계 처음 시작함
            self.info["events"] = self.info["events"][:-1]

        # 첫단계 포함, 사건 중간에 재시작
        self.info["events"][-1]["original_history"] = []
        self.info["events"][-1]["summarized_history"] = []
        self.info["events"][-1]["is_end"] = False
        self.info["ending"] = None

    # utils
    def save(self) -> None:
        fn = self.story_name + ".json"
        dump_json(self.info, os.path.join(path.play_info_dir, self.username, fn))

    @classmethod
    def load(cls, username: str, story_name: str) -> dict:
        return cls(
            username=username,
            story_name=story_name,
            info=load_json(os.path.join(path.play_info_dir, username, story_name + ".json")),
        )

    @classmethod
    def remove(cls, username: str, story_name: str) -> None:
        os.remove(os.path.join(path.play_info_dir, username, story_name + ".json"))

    @classmethod
    def get_story_list(cls, username: Optional[str], preprocess: bool = False) -> list[str]:
        if not isinstance(username, str):
            return []

        stories = [
            (
                os.path.splitext(fn)[0].split("_", 1)[1].replace("_", " ")
                if preprocess
                else os.path.splitext(fn)[0]
            )
            for fn in os.listdir(os.path.join(path.play_info_dir, username))
            if fn.endswith(".json")
        ]
        return stories
