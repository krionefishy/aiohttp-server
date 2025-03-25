import typing

from app.store.vk_api.dataclasses import Update
from app.store.vk_api.dataclasses import Message
if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            if update.type == "message_new":
                message = Message(
                    user_id=update.object.message.from_id,
                    text=update.object.message.text
                )
                # Здесь можно добавить логику обработки сообщений
                # Например:
                if message.text.lower() == "kek":
                    await self.app.store.vk_api.send_message(
                        Message(
                            user_id=message.user_id,
                            text="Pupupu"
                        )
                    )
