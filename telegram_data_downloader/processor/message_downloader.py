import asyncio
import logging
import typing

import telethon
from telethon.tl.types import (
    DocumentAttributeAudio,
    DocumentAttributeSticker,
    DocumentAttributeVideo,
    DocumentEmpty,
    Message,
    MessageMediaDocument,
    MessageMediaPhoto,
    PeerUser,
    PeerChannel,
    PeerChat,
    TypeInputPeer,
    TypePeer,
    ReactionEmoji,
    Channel,
)
from telethon.tl.types.messages import MessageReactionsList

from ..dict_types.dialog import DialogMetadata
from ..dict_types.message import MessageAttributes, MessageType, PeerID

logger = logging.getLogger(__name__)


class DialogReader(typing.Protocol):
    def read_dialog(self, dialog_id: int) -> DialogMetadata: ...


class MessageWriter(typing.Protocol):
    def write_messages(
        self, dialog: DialogMetadata, messages: list[MessageAttributes]
    ) -> None: ...


class MessageDownloader:
    def __init__(
        self,
        client: telethon.TelegramClient,
        dialog_reader: DialogReader,
        message_writer: MessageWriter,
        *,
        reactions_limit_per_message: int,
    ) -> None:
        self.client = client
        self.dialog_reader = dialog_reader
        self.message_writer = message_writer
        self.reactions_limit_per_message = reactions_limit_per_message
        self._semaphore = asyncio.Semaphore(5)

    @property
    def concurrent_dialog_downloads(self) -> int:
        return self._semaphore._value

    @concurrent_dialog_downloads.setter
    def concurrent_dialog_downloads(self, value: int) -> None:
        self._semaphore = asyncio.Semaphore(value)

    @staticmethod
    def _get_peer_id(peer: TypePeer) -> int:
        if isinstance(peer, PeerUser):
            return peer.user_id
        elif isinstance(peer, PeerChat):
            return peer.chat_id
        elif isinstance(peer, PeerChannel):
            return peer.channel_id
        else:
            raise ValueError(f"Unknown peer type: {peer}")

    def _reformat_message(self, message: Message) -> MessageAttributes:
        fwd_from = (
            self._get_peer_id(message.fwd_from.from_id)
            if message.fwd_from and message.fwd_from.from_id
            else None
        )
        from_id = self._get_peer_id(message.from_id) if message.from_id else None

        msg_attributes: MessageAttributes = {
            "id": message.id,
            "date": message.date,
            "from_id": PeerID(from_id) if from_id else None,
            "fwd_from": PeerID(fwd_from) if fwd_from else None,
            "message": message.message,
            "type": MessageType.TEXT,
            "duration": None,
            "to_id": (
                PeerID(self._get_peer_id(message.peer_id)) if message.peer_id else None
            ),
            "reactions": {},
        }

        if media := message.media:
            # For stickers, videos, and voice messages
            if (
                isinstance(media, MessageMediaDocument)
                and media.document
                and not isinstance(media.document, DocumentEmpty)
            ):
                for attribute in media.document.attributes:
                    if isinstance(attribute, DocumentAttributeSticker):
                        msg_attributes["message"] = attribute.alt
                        msg_attributes["type"] = MessageType.STICKER
                        break

                    elif isinstance(attribute, DocumentAttributeVideo):
                        msg_attributes["duration"] = attribute.duration
                        msg_attributes["type"] = MessageType.VIDEO
                        break

                    elif (
                        isinstance(attribute, DocumentAttributeAudio)
                        and attribute.voice
                    ):
                        msg_attributes["duration"] = attribute.duration
                        msg_attributes["type"] = MessageType.VOICE
                        break
            elif isinstance(message.media, MessageMediaPhoto):
                msg_attributes["type"] = MessageType.PHOTO

        return msg_attributes

    async def _get_message_reactions(
        self, message: Message, dialog_peer: TypeInputPeer
    ) -> dict[PeerID, ReactionEmoji]:
        # ! Doesn't work for broadcast channels.
        try:
            result: MessageReactionsList = await self.client(
                telethon.functions.messages.GetMessageReactionsListRequest(
                    peer=dialog_peer,
                    id=message.id,
                    limit=self.reactions_limit_per_message,
                )
            )  # type: ignore
        except telethon.errors.MsgIdInvalidError:
            logger.debug(f"message {message.id} not found")
            reactions = {}
        except telethon.errors.BroadcastForbiddenError:
            logger.debug("channel is broadcast: cannot retrieve reactions from message")
            reactions = {}
        else:
            reaction_objects = result.reactions
            reactions = {
                PeerID(
                    self._get_peer_id(reaction_object.peer_id)
                ): reaction_object.reaction
                for reaction_object in reaction_objects
                if isinstance(reaction_object.reaction, ReactionEmoji)
            }

        return reactions

    async def _download_dialog(self, dialog: DialogMetadata, msg_limit: int) -> None:
        logger.debug(f"downloading dialog {dialog['id']}")
        try:
            tg_entity = await self.client.get_entity(dialog["id"])
            messages = await self.client.get_messages(tg_entity, limit=msg_limit)
        except ValueError:
            logger.error(f"no such ID found: #{dialog['id']}")

            username = None
            try:
                dialog_metadata = self.dialog_reader.read_dialog(dialog["id"])
            except FileNotFoundError:
                logger.error(f"dialog {dialog['id']} not found")
                raise

            if (
                "users" in dialog_metadata
                and len(dialog_metadata["users"]) == 1
                and "username" in dialog_metadata["users"][0]
            ):
                username = dialog_metadata["users"][0]["username"]
            else:
                logger.error(f"error for dialog #{dialog['id']}")
                return

            if not username:
                # * user found, but username is empty
                logger.error(f"error for dialog #{dialog['id']}")
                raise ValueError("username is empty")

            logger.debug(f"init dialog {dialog['id']} through username {username}")
            _ = await self.client.get_entity(username)
            tg_entity = await self.client.get_entity(dialog["id"])
            messages = await self.client.get_messages(tg_entity, limit=msg_limit)

        if not messages:
            return
        messages = typing.cast(list[telethon.types.Message], messages)

        dialog_messages = []
        for m in messages:
            msg_attrs = self._reformat_message(m)
            if isinstance(tg_entity, Channel) and tg_entity.broadcast:
                # * avoid getting reactions for broadcast channels
                continue
            peer = typing.cast(
                TypeInputPeer, telethon.utils.get_peer(dialog["id"])
            )  # * cast because dialog is TypeInputPeer
            msg_attrs["reactions"] = {
                k: v.emoticon
                for k, v in (await self._get_message_reactions(m, peer)).items()
            }
            dialog_messages.append(msg_attrs)

        self.message_writer.write_messages(dialog, dialog_messages)

    async def _semaphored_download_dialog(self, *args, **kwargs):
        async with self._semaphore:
            await self._download_dialog(*args, **kwargs)

    async def download_dialogs(
        self, dialogs: list[DialogMetadata], msg_limit: int
    ) -> None:
        tasks = []
        for dialog in dialogs:
            tasks.append(self._semaphored_download_dialog(dialog, msg_limit))
        await asyncio.gather(*tasks)
        return
