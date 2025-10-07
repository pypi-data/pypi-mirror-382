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

from typing import Union

import pyrogram
from pyrogram import raw

from ..messages.inline_session import get_session


class UnpinChatMessage:
    async def unpin_chat_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int = 0,
        business_connection_id: str = None,
    ) -> bool:
        """Unpin a message in a group, channel or your own chat.
        You must be an administrator in the chat for this to work and must have the "can_pin_messages" admin
        right in the supergroup or "can_edit_messages" admin right in the channel.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                You can also use chat public link in form of *t.me/<username>* (str).

            message_id (``int``, *optional*):
                Identifier of a message to unpin.
                Required if ``business_connection_id`` is specified.
                If not specified, the most recent pinned message (by sending date) will be unpinned.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be unpinned.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.unpin_chat_message(chat_id, message_id)
        """
        rpc = raw.functions.messages.UpdatePinnedMessage(
            peer=await self.resolve_peer(chat_id), id=message_id, unpin=True
        )

        if business_connection_id:
            await self.invoke(
                raw.functions.InvokeWithBusinessConnection(
                    query=rpc, connection_id=business_connection_id
                )
            )
        else:
            await self.invoke(rpc)

        return True
