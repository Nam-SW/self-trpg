def get_default_user_info() -> dict:
    """유저 정보 기본 틀 반환

    Returns:
        dict: 유저 정보 기본 틀
    """
    # TODO: config 정리 필요. 세계관 정보 / 유저 정보 확실히 분리.
    return {
        "main_theme": None,  # 메인 주제
        "keywords": None,  # 서브 키워드
        "worldview": None,  # 세계관
        "chat_history": [],
        "event_history": [],  # 사건 요약 / 월드 정보에 포함하는게 좋으려나
        "user_info": {
            "user_role": None,  # 유저의 역할 / 변화할 수도 있으니 정산에 추가해야할 듯
            "user_sex": None,  # 유저 성별
            "current_location": None,  # 최근 위치
            "hp": 100,  # 체력
            "mental": 100,  # 정신력
            "max_hp": 100,
            "max_mental": 100,
            "skills": [],  # 보유 기술
            "items": [],  # 보유 아이템
            "companion": [],  # 동료
        },
    }


def get_new_user(
    worldview: str,
    sex: str,
    role: str,
    location: str,
    starting_point: str,
) -> dict:
    info = get_default_user_info()
    info["worldview"] = worldview
    info["user_info"]["sex"] = sex
    info["user_role"] = role
    info["user_info"]["current_location"] = location
    info["user_info"]["prev_major_event"] = [starting_point]
    return info
