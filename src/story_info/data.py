from typing import Optional, TypedDict


class Chat(TypedDict):
    role: str  # 발화자
    message: str  # 발화내용


class Companion(TypedDict):
    name: str  # 이름
    info: str  # 설명


class UserInfo(TypedDict):
    role: str  # 유저의 역할
    sex: str  # 유저 성별
    location: str  # 최근 위치
    hp: int = 100  # 체력
    mental: int = 100  # 정신력
    max_hp: int = 100  # 최대 체력
    max_mental: int = 100  # 최대 정신력
    characteristics: list[str] = []  # 특성
    skills: list[str] = []  # 보유 기술
    inventory: list[str] = []  # 보유 아이템
    companion: list[str] = []  # dict[str, str]: 동료


class EventInfo(TypedDict):
    original_history: list[Chat] = []  # 현재 사건의 대화 내역
    summarized_history: list[Chat] = []  # 현재 사건의 대화 요약 내역
    prev_summary: str  # 이전 사건의 결과 요약
    user_info: UserInfo  # 현재 사건의 유저 상태(이전 사건 결과)
    is_end: bool = False  # 사건 종료 여부


class StoryInfo(TypedDict):
    main_theme: str  # 메인 테마
    keywords: str  # 키워드
    worldview: str  # 세계관
    limit_event: int = 50  # 최대 사건 개수
    events: list[EventInfo]  # 사건 정보
    ending: Optional[str] = None  # 엔딩
