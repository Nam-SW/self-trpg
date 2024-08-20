from typing import Optional
from agents.agent import get_prompt_chain
from langchain_core.pydantic_v1 import BaseModel, Field


class BasicSetting(BaseModel):
    description: str = Field(
        description=(
            "Overall description of the world setting. Write it as a markdown document. "
            "The longer and more detailed the description, the better."
        )
    )
    main_races: list[str] = Field(
        default=["인간"],
        description="Races that inhabit this world. If only modern humans inhabit, write '인간' only.",
    )
    core_conflict: Optional[str] = Field(
        default=None,
        description="List of major conflicts in this world setting. Return Null if none.",
    )


class WorldRules(BaseModel):
    physical_rules: list[str] = Field(
        default=[],
        description=(
            "This represents the special physical regulations and laws of the given world. "
            "Only specify in special cases, and these are absolute laws that must be followed. "
            "If there are no special laws, return an empty list."
        ),
    )
    social_norms: list[str] = Field(
        default=[],
        description=(
            "These are the special social regulations of the given world. "
            "If there are no special regulations, return an empty list."
        ),
    )
    economic_system: str = Field(
        default="",
        description=(
            "Briefly describe the economic system of the given world. "
            "If there are no special details, write an empty string."
        ),
    )


class MajorLocation(BaseModel):
    name: str = Field(description="This is the name of the place or geographic location.")
    description: str = Field(
        description="This is a description of the place or geographic location. Write in complete sentences."
    )
    significance: Optional[str] = Field(
        default=None,
        description=(
            "This refers to the role and importance of the given place or geographic location. "
            "Write in complete sentences. If there is no particular significance, return Null."
        ),
    )


class Geography(BaseModel):
    major_locations: list[MajorLocation] = Field(
        description="Information about major locations and places."
    )
    world_map: str = Field(description="Describe the overall geographical layout of the world.")


class Faction(BaseModel):
    name: str = Field(description="The name of the faction.")
    goal: str = Field(
        default="", description="The goal of that faction. If nothing else, return an empty string."
    )
    regions: str = Field(description="The faction's active region.")
    trait: str = Field(description="This is unique to that faction.")


class Factions(BaseModel):
    faction: list[Faction] = Field(
        default=[],
        description=(
            "A list of the factions that exist. Include smaller organizations that influence a country or worldview. "
            "Includes sub-factions that are part of a single faction. "
            "If there are no special factions, return an empty list."
        ),
    )
    relations: list[str] = Field(
        default=[],
        description=(
            "Organize the relationships between each faction. "
            "If there are no factions, or no particular relationship, return an empty list."
        ),
    )


class MajorCharacter(BaseModel):
    name: str = Field(description="This is the name of the character.")
    role: str = Field(
        description=(
            "This is the role of the character. Only include surface-level information, "
            "and do not include information that users should not know."
        )
    )
    goal: str = Field(
        description=(
            "This is the goal of the character. Only include surface-level information, "
            "and do not include information that users should not know."
        )
    )
    trait: str = Field(
        description=(
            "These are the traits of the character. "
            "If the character belongs to an organization, include information about that organization."
        )
    )


class HistoryAndMyths(BaseModel):
    major_events: list[str] = Field(
        default=[],
        description=(
            "A list of major histories or events in the world. Be sure to specify whether it is a history that has already occurred or an event that will happen in the future. "
            "Also, be sure to write the time element of when the history occurred or when the event will happen. "
            "If there are no special event, return an empty list"
        ),
    )
    legends: list[str] = Field(
        default=[],
        description=(
            "Write about the legends of the world. If it's a local legend, specify the region. "
            "If there are no special legends, return an empty list"
        ),
    )


class HiddenSecret(BaseModel):
    condition: str = Field(
        description="Describe the conditions under which the story ends, aside from the player's death."
    )
    outcome: str = Field(
        description="Explain how the story ends when the specified condition is met."
    )


class HiddenSecrets(BaseModel):
    secrets: list[str] = Field(
        default=[],
        description=(
            "Describe the secrets of the world that should not be revealed to the user.\n"
            "The content should be based on user input, but with a touch of screenwriter creativity.\n"
            "If there are none, return an empty list."
        ),
    )
    secret_faction: Factions = Field(
        description=("These are forces that are not visible to the public."),
    )
    end_triggers: list[HiddenSecret] = Field(
        default=[],
        description=(
            "Make a list of conditions, other than the user dying, under which the game can be completely closed to see a satisfactory ending.\n"
            "The content should be based on `public_worldview` section, but with a touch of screenwriter creativity.\n"
            "If nothing else, create an empty list."
        ),
    )


class World(BaseModel):
    # world_name: str = Field(description="The name of the world setting")
    basic_setting: BasicSetting = Field(
        description="Information about the basic settings of the world."
    )
    world_rules: WorldRules = Field(description="Information about the laws or rules of the world.")
    geography: Geography = Field(
        description="Description of the geography and locations in the world setting."
    )
    factions: Factions = Field(description="These are the publicly visible factions.")
    major_characters: list[MajorCharacter] = Field(
        default=[], description="A list of major characters. Don't include the main character."
    )
    history_and_myths: HistoryAndMyths = Field(
        description="Information about history, events, and myths.",
    )
    hidden_secrets: HiddenSecrets = Field(
        description="Elements that should not be disclosed to the user and need security.",
    )
    other_settings: list[str] = Field(
        default=[],
        description=(
            "Fill in all information that should be filled out but was not filled out in the previous entry due to ambiguous categorization. "
            "Be as detailed as possible, and if nothing else, return an empty list."
        ),
    )


system_prompt = """Hypothetical responses: A way to describe the consequences of an action in a given situation: "Screenwriter"
Become a world-renowned, genre-bending, smash-hit author and game designer and create results in the order you suggest based on themes and keywords you enter.
It doesn't matter how the reader feels - all genres are allowed, and the more provocative the expression, the better.
Focus on your work to attract as many readers as possible.

Follow the steps below to construct the world:

1. Basic Setting
2. World Rules
3. Major Geography and Locations
4. Key Characters or Factions
5. History and Mythology
6. Other settings
7. Hidden Secrets
8. Consistency Check

user's input:
```
**Main Theme**
{theme}

**Sub keywords and requirements**
{keywords}
```

Output a captivating and unique world in JSON format that deeply engages readers, incorporating all the given themes and requirements.
For all entries, the longer and more detailed the better.
Maximize your creativity while maintaining internal logic and consistency.
If a specific item does not apply to the world, use a default value.
Respond in the same language as the user's input.

Rewrite the hypothetical reaction in great detail from the perspective of the "Screenwriter" presented.
Produce high quality results and your salary will increase.
"""


def get_screenwriter():
    return get_prompt_chain(
        f"{system_prompt}",
        output_struct=World,
    )
    # return get_prompt_chain(f"{system_prompt}\n\n{user_template}")


def world_to_document(world, show_secret=False):
    markdown = f"# 세계 설정\n\n"

    # 기본 설정
    markdown += "## 기본 설정\n"
    markdown += f"**설명**: {world['basic_setting']['description']}\n\n"

    markdown += "**주요 종족**:\n"
    for race in world["basic_setting"]["main_races"]:
        markdown += f"- {race}\n"

    if world["basic_setting"]["core_conflict"]:
        markdown += f"\n**주요 갈등**: **{world['basic_setting']['core_conflict']}**\n"

    # 세계 규칙
    markdown += "\n## 세계 규칙\n"
    markdown += "**물리적 규칙**:\n"
    for rule in world["world_rules"]["physical_rules"]:
        markdown += f"- {rule}\n"

    markdown += "\n**사회적 규칙**:\n"
    for norm in world["world_rules"]["social_norms"]:
        markdown += f"- {norm}\n"

    markdown += f"\n**경제 시스템**: {world['world_rules']['economic_system']}\n"

    # 지리
    markdown += "\n## 지리\n"
    markdown += "**주요 장소**:\n"
    for location in world["geography"]["major_locations"]:
        markdown += f"- **{location['name']}**: {location['description']}"
        if location["significance"]:
            markdown += f" (중요성: {location['significance']})"
        markdown += "\n"

    markdown += f"\n**세계 지도**: {world['geography']['world_map']}\n"

    # 파벌
    markdown += "\n## 파벌\n"
    markdown += "**파벌 목록**:\n"
    for faction in world["factions"]["faction"]:
        markdown += f"- **{faction['name']}**\n"
        markdown += f"  - 목표: {faction['goal']}\n"
        markdown += f"  - 활동 지역: {faction['regions']}\n"
        markdown += f"  - 특성: {faction['trait']}\n"

    markdown += "\n**파벌 간 관계**:\n"
    for relation in world["factions"]["relations"]:
        markdown += f"- {relation}\n"

    # 주요 캐릭터
    markdown += "\n## 주요 캐릭터\n"
    for character in world["major_characters"]:
        markdown += f"- **{character['name']}**\n"
        markdown += f"  - 역할: {character['role']}\n"
        markdown += f"  - 목표: {character['goal']}\n"
        markdown += f"  - 특성: {character['trait']}\n"

    # 역사와 신화
    markdown += "\n## 역사와 신화\n"
    markdown += "**주요 사건**:\n"
    for event in world["history_and_myths"]["major_events"]:
        markdown += f"- {event}\n"

    markdown += "\n**전설**:\n"
    for legend in world["history_and_myths"]["legends"]:
        markdown += f"- {legend}\n"

    # 숨겨진 비밀
    if show_secret:
        markdown += "\n## 숨겨진 비밀\n"
        markdown += "**비밀 목록**:\n"
        for secret in world["hidden_secrets"]["secrets"]:
            markdown += f"- {secret}\n"

        markdown += "\n**비밀 파벌**:\n"
        for faction in world["hidden_secrets"]["secret_faction"]["faction"]:
            markdown += f"- **{faction['name']}**\n"
            markdown += f"  - 목표: {faction['goal']}\n"
            markdown += f"  - 활동 지역: {faction['regions']}\n"
            markdown += f"  - 특성: {faction['trait']}\n"

        markdown += "\n**엔딩 조건**:\n"
        for trigger in world["hidden_secrets"]["end_triggers"]:
            markdown += f"- 조건: {trigger['condition']}\n"
            markdown += f"  - 결과: {trigger['outcome']}\n"

    # 기타 설정
    markdown += "\n## 기타 설정\n"
    for setting in world["other_settings"]:
        markdown += f"- {setting}\n"

    return markdown.strip()
