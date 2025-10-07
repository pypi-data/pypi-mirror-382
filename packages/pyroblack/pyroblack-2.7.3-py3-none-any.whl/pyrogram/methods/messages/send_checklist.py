#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import logging
from datetime import datetime
from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils

log = logging.getLogger(__name__)


class SendChecklist:
    async def send_checklist(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        title: str,
        tasks: List["types.InputChecklistTask"],
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        others_can_add_tasks: Optional[bool] = None,
        others_can_mark_tasks_as_done: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        effect_id: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        schedule_date: Optional[datetime] = None,
        paid_message_star_count: int = None,
    ) -> "types.Message":
        """Send a new checklist.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            title (``str``):
                Title of the checklist.

            tasks (List of ``str``):
                List of tasks in the checklist, 1-30 tasks.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                The parse mode to use for the checklist.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the checklist title.

            others_can_add_tasks (``bool``, *optional*):
                True, if other users can add tasks to the list.

            others_can_mark_tasks_as_done (``bool``, *optional*):
                True, if other users can mark tasks as done or not done.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent checklist message is returned.

        Example:
            .. code-block:: python

                await client.send_checklist(
                    chat_id=message.chat.id,
                    title="To do",
                    tasks=[
                        types.InputChecklistTask(id=1, text="Task 1"),
                        types.InputChecklistTask(id=2, text="Task 2")
                    ]
                )
        """
        title, entities = (
            await utils.parse_text_entities(self, title, parse_mode, entities)
        ).values()

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=raw.types.InputMediaTodo(
                    todo=raw.types.TodoList(
                        title=raw.types.TextWithEntities(
                            text=title, entities=entities or []
                        ),
                        list=[await task.write(self) for task in tasks],
                        others_can_append=others_can_add_tasks,
                        others_can_complete=others_can_mark_tasks_as_done,
                    )
                ),
                message="",
                silent=disable_notification,
                reply_to=await utils.get_reply_to(
                    self, reply_parameters, message_thread_id
                ),
                random_id=self.rnd_id(),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                allow_paid_stars=paid_message_star_count,
                effect=effect_id,
            )
        )

        messages = await utils.parse_messages(client=self, messages=r)

        return messages[0] if messages else None
