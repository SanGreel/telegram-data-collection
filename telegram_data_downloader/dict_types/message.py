from datetime import datetime
from enum import Enum
from typing import NewType, Optional, TypedDict

PeerID = NewType("PeerID", int)


class MessageType(Enum):
    TEXT = "text"
    STICKER = "sticker"
    VIDEO = "video"
    VOICE = "voice"
    PHOTO = "photo"


class MessageAttributes(TypedDict):
    id: int
    date: Optional[datetime]
    message: str
    type: MessageType
    duration: Optional[float]
    from_id: Optional[PeerID]
    to_id: Optional[PeerID]
    fwd_from: Optional[PeerID]
    reactions: dict[PeerID, str]
