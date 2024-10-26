import asyncio
import logging
import typing

import telethon
from telethon.tl import types as tl_types

from ..dict_types.dialog import DialogMetadata
from ..dict_types.message import MessageAttributes, MessageType, PeerID
from ..utils import async_retry


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

    def _reformat_message(self, message: tl_types.Message) -> MessageAttributes:
        fwd_from = (
            telethon.utils.get_peer_id(message.fwd_from.from_id)
            if message.fwd_from and message.fwd_from.from_id
            else None
        )
        from_id = (
            telethon.utils.get_peer_id(message.from_id) if message.from_id else None
        )

        msg_attributes: MessageAttributes = {
            "id": message.id,
            "date": message.date,
            "from_id": PeerID(from_id) if from_id else None,
            "fwd_from": PeerID(fwd_from) if fwd_from else None,
            "message": message.message,
            "type": MessageType.TEXT,
            "duration": None,
            "to_id": (
                PeerID(telethon.utils.get_peer_id(message.peer_id))
                if message.peer_id
                else None
            ),
            "reactions": {},
        }

        if media := message.media:
            # For stickers, videos, and voice messages
            if (
                isinstance(media, tl_types.MessageMediaDocument)
                and media.document
                and not isinstance(media.document, tl_types.DocumentEmpty)
            ):
                for attribute in media.document.attributes:
                    if isinstance(attribute, tl_types.DocumentAttributeSticker):
                        msg_attributes["message"] = attribute.alt
                        msg_attributes["type"] = MessageType.STICKER
                        break

                    elif isinstance(attribute, tl_types.DocumentAttributeVideo):
                        msg_attributes["duration"] = attribute.duration
                        msg_attributes["type"] = MessageType.VIDEO
                        break

                    elif (
                        isinstance(attribute, tl_types.DocumentAttributeAudio)
                        and attribute.voice
                    ):
                        msg_attributes["duration"] = attribute.duration
                        msg_attributes["type"] = MessageType.VOICE
                        break
            elif isinstance(message.media, tl_types.MessageMediaPhoto):
                msg_attributes["type"] = MessageType.PHOTO

        return msg_attributes

    @async_retry(
        telethon.errors.common.InvalidBufferError,
        base_sleep_time=5.0,
        max_tries=5,
    )
    async def _get_message_reactions(
        self, message: tl_types.Message, dialog_peer: tl_types.TypeInputPeer
    ) -> dict[PeerID, tl_types.ReactionEmoji]:
        try:
            result: tl_types.messages.MessageReactionsList = await self.client(
                telethon.functions.messages.GetMessageReactionsListRequest(
                    peer=dialog_peer,
                    id=message.id,
                    limit=self.reactions_limit_per_message,
                )
            )  # type: ignore
        except telethon.errors.BroadcastForbiddenError:
            # logger.debug("channel is broadcast: cannot retrieve reactions from message")
            reactions = {}
        except telethon.errors.MsgIdInvalidError:
            # logger.debug(f"message {message.id} not found")
            reactions = {}
        else:
            reaction_objects = result.reactions
            reactions = {
                PeerID(
                    telethon.utils.get_peer_id(reaction_object.peer_id)
                ): reaction_object.reaction
                for reaction_object in reaction_objects
                if isinstance(reaction_object.reaction, tl_types.ReactionEmoji)
            }

        return reactions

    async def _get_message_iterator(
        self, dialog: DialogMetadata, msg_limit: int
    ) -> typing.AsyncIterator[tl_types.Message]:
        logger.debug(f"dialog #{dialog['id']}: creating message iterator")
        try:
            tg_entity = await self.client.get_entity(dialog["id"])
        except ValueError:
            logger.error(f"dialog #{dialog['id']}: no such ID found")
            logger.info(f"init dialog {dialog['id']} through member username")

            username = None
            try:
                dialog_metadata = self.dialog_reader.read_dialog(dialog["id"])
            except FileNotFoundError:
                logger.error(f"dialog #{dialog['id']}: not found")
                raise

            if (
                "users" in dialog_metadata
                and len(dialog_metadata["users"]) == 1
                and "username" in dialog_metadata["users"][0]
            ):
                username = dialog_metadata["users"][0]["username"]
            else:
                logger.error(f"dialog #{dialog['id']}: not a private chat")
                return

            if not username:
                # * user found, but username is empty
                logger.error(
                    f"dialog #{dialog['id']}: single user found, but username is empty"
                )
                raise ValueError("username is empty")

            tg_entity = await self.client.get_input_entity(username)
        except Exception as e:
            logger.error(f"dialog #{dialog['id']}: {e}")
            return

        if isinstance(tg_entity, list):
            tg_entity = tg_entity[0]
        async for message in self.client.iter_messages(
            tg_entity, limit=msg_limit, wait_time=5
        ):
            yield message

    async def _download_dialog(self, dialog: DialogMetadata, msg_limit: int) -> None:
        logger.info(f"dialog #{dialog['id']}: downloading messages...")
        dialog_messages: list[MessageAttributes] = []

        is_broadcast_channel: bool | None = None
        msg_count = 0

        async for m in self._get_message_iterator(dialog, msg_limit):
            msg_count += 1
            if msg_count % 1000 == 0:
                logger.debug(
                    f"dialog #{dialog['id']}: processing message number {msg_count}"
                )

            msg_attrs = self._reformat_message(m)

            if is_broadcast_channel is None and isinstance(
                m.peer_id, tl_types.PeerChannel
            ):
                channel = await self.client.get_entity(m.peer_id)
                assert isinstance(channel, tl_types.Channel)
                is_broadcast_channel = channel.broadcast
            if not is_broadcast_channel:
                # * avoid getting reactions for broadcast channels
                peer = typing.cast(
                    tl_types.TypeInputPeer, telethon.utils.get_peer(dialog["id"])
                )  # * cast because dialog is tl_types.TypeInputPeer
                msg_attrs["reactions"] = {
                    k: v.emoticon
                    for k, v in (await self._get_message_reactions(m, peer)).items()
                }

            dialog_messages.append(msg_attrs)

        self.message_writer.write_messages(dialog, dialog_messages)
        logger.info(f"dialog #{dialog['id']}: messages downloaded")

    async def _semaphored_download_dialog(self, *args, **kwargs):
        async with self._semaphore:
            await self._download_dialog(*args, **kwargs)

    async def download_dialogs(
        self, dialogs: list[DialogMetadata], msg_limit: int
    ) -> None:
        logger.info(f"downloading messages from {len(dialogs)} dialogs...")
        tasks = []
        for dialog in dialogs:
            # TODO: up for debate: move semaphored download to a separate entity, possibly a decorator
            tasks.append(self._semaphored_download_dialog(dialog, msg_limit))
        await asyncio.gather(*tasks)
        logger.info("all dialogs downloaded")
        return
