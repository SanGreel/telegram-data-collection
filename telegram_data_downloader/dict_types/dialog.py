from enum import Enum
from typing import TypedDict, Optional


class DialogType(Enum):
    PRIVATE = "private"
    GROUP = "group"
    CHANNEL = "channel"
    UNKNOWN = "unknown"


class DialogMemberData(TypedDict):
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: str
    phone: Optional[str]


class DialogMetadata(TypedDict):
    id: int
    name: str
    type: DialogType
    users: list[DialogMemberData]
