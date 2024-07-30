def get_default_user_info() -> dict:
    """유저 정보 기본 틀 반환

    Returns:
        dict: 유저 정보 기본 틀
    """
    # TODO: config 정리 필요. 세계관 정보 / 유저 정보 확실히 분리.
    return {
        "main_theme": None,  # str: 메인 주제
        "keywords": None,  # str: 서브 키워드
        "worldview": None,  # str: 세계관
        "chat_history": [],  # list[list[str]]: 전체 채팅 history
        "event_history": [],  # list[str]: 사건 요약 / 월드 정보에 포함하는게 좋으려나
        "user_info": {
            "role": None,  # str: 유저의 역할 / 변화할 수도 있으니 정산에 추가해야할 듯
            "sex": None,  # str: 유저 성별
            "location": None,  # str: 최근 위치
            "hp": 100,  # int: 체력
            "mental": 100,  # int: 정신력
            "max_hp": 100,  # int: 최대 체력
            "max_mental": 100,  # int: 최대 정신력
            "characteristics": [],  # list[str]: 특성
            "skills": [],  # list[str]: 보유 기술
            "inventory": [],  # list[str]: 보유 아이템
            "companion": [],  # dict[str, str]: 동료
        },
    }


def get_new_user(
    main_theme: str,
    keywords: str,
    worldview: str,
    sex: str,
    role: str,
    location: str,
    hp: int,
    mental: int,
    max_hp: int,
    max_mental: int,
    characteristics: list[str],
    skills: list[str],
    inventory: list[str],
    start_event: str,
) -> dict:
    info = get_default_user_info()

    # 세계 정보
    info["main_theme"] = main_theme
    info["keywords"] = keywords
    info["worldview"] = worldview
    info["event_history"] = [start_event]

    # 유저 정보
    info["user_info"]["sex"] = sex
    info["user_info"]["role"] = role
    info["user_info"]["location"] = location
    info["user_info"]["hp"] = hp
    info["user_info"]["mental"] = mental
    info["user_info"]["max_hp"] = max_hp
    info["user_info"]["max_mental"] = max_mental
    info["user_info"]["characteristics"] = characteristics
    info["user_info"]["skills"] = skills
    info["user_info"]["inventory"] = inventory

    return info
