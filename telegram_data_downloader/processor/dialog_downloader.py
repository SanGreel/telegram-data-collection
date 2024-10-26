import asyncio
import logging
import typing

import telethon
from telethon.tl import custom as tl_custom
from telethon.tl import types as tl_types

from ..dict_types.dialog import DialogMemberData, DialogMetadata, DialogType

logger = logging.getLogger(__name__)


class DialogSaver(typing.Protocol):
    def write_dialog(self, data: DialogMetadata) -> None: ...


class DialogDownloader:
    def __init__(
        self,
        telegram_client: telethon.TelegramClient,
        dialog_saver: DialogSaver,
    ):
        self.dialog_saver = dialog_saver
        self.client = telegram_client

    async def save_dialogs(self, dialogs_limit: int | None) -> bool:
        logger.debug("retrieving dialog list...")
        dialogs: list[tl_custom.Dialog] = await self.client.get_dialogs(
            limit=dialogs_limit
        )
        logger.info(f"found {len(dialogs)} dialogs")

        tasks = []
        # * process each dialog asynchronously, therefore increasing throughput
        for dialog in typing.cast(list[tl_custom.Dialog], dialogs):
            task = asyncio.create_task(self._save_dialog(dialog))
            tasks.append(task)

        logger.debug("gathering dialog saving tasks...")
        await asyncio.gather(*tasks)
        logger.info("dialogs list saved successfully")
        return True

    async def _save_dialog(self, dialog: tl_custom.Dialog):
        dialog_id = dialog.id
        dialog_name = dialog.name
        dialog_members: list[DialogMemberData] = []

        logger.info(f"dialog #{dialog_id}: starting processing...")

        type_to_enum = {
            dialog.is_user: DialogType.PRIVATE,
            dialog.is_group: DialogType.GROUP,
            dialog.is_channel: DialogType.CHANNEL,
        }
        dialog_type = type_to_enum.get(True, DialogType.UNKNOWN)

        # TODO: remember prev dialog type
        # dialog_type = ""
        # if dialog.is_user:
        #     dialog_type = "Private dialog"
        # elif dialog.is_group:
        #     dialog_type = "Group"
        # elif dialog.is_channel:
        #     dialog_type = "Channel"

        logger.debug(f"dialog #{dialog_id}: getting participants...")
        try:
            users: list[tl_types.User] = await self.client.get_participants(dialog)
        except telethon.errors.ChatAdminRequiredError as e:
            logger.error(
                f"dialog #{dialog_id}: getting participants: admin required: {e}"
            )
        except telethon.errors.ChannelPrivateError as e:
            logger.error(
                f"dialog #{dialog_id}: getting participants: channel private: {e}"
            )
        except telethon.errors.ChannelInvalidError as e:
            logger.error(
                f"dialog #{dialog_id}: getting participants: channel invalid: {e}"
            )
        except telethon.errors.RPCError as e:
            logger.error(
                f"dialog #{dialog_id}: getting participants: unknown error: {e}"
            )
        else:
            logger.debug(f"dialog #{dialog_id}: processing participants...")
            dialog_members = [
                DialogMemberData(
                    user_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    phone=user.phone,
                )
                for user in users
                if user.username is not None
            ]  # * list comprehension is generally faster than for loop

        self.dialog_saver.write_dialog(
            DialogMetadata(
                id=dialog_id,
                name=dialog_name,
                type=dialog_type,
                users=dialog_members,
            )
        )

        logger.info(f"dialog #{dialog_id}: successfully saved")
