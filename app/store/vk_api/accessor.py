import typing
from urllib.parse import urlencode, urljoin

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message
from app.store.vk_api.poller import Poller
from app.store.vk_api.dataclasses import *

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        # TODO: добавить создание aiohttp ClientSession,
        #  получить данные о long poll сервере с помощью метода groups.getLongPollServer
        #  вызвать метод start у Poller
        self.session = ClientSession
        await self._get_long_poll_service()
        self.poller = Poller(app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        # TODO: закрыть сессию и завершить поллер
        if self.poller():
            await self.poller.stop()
        if self.session and not self.session.closed:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        if not self.session:
            raise RuntimeError("session is not running")

        params = {
            "group_id": self.app.config.bot.group_id,
            "access_token": self.app.config.bot.token,
        }
        url = self._build_query("https://api.vk.com", "groups.getLongPollServer", params)

        async with self.session.get(url) as resp:
            data = await resp.json()
            if "response" not in data:
                raise RuntimeError(f"Failed to get long poll server: {data}")
            
            self.key = data["response"]["key"]
            self.server = data["response"]["server"]
            self.ts = data["response"]["ts"]

        

    async def poll(self):
        if not (self.server and self.key and self.ts):
            await self._get_long_poll_service()

        params = {
            "act": "a_check",
            "key": self.key,
            "ts": self.ts,
            "wait": 30
        }

        try:
            async with self.session.get(f"{self.server}?{urlencode(params)}") as resp:
                data = await resp.json()
                
                if "failed" in data:
                    if data["failed"] == 1:
                        self.ts = data["ts"]
                    else:
                        await self._get_long_poll_service()
                    return
                
                self.ts = data["ts"]
                updates = []
                for event in data.get("updates", []):
                    if event["type"] == "message_new":
                        msg = event["object"]["message"]
                        updates.append(Update(
                            type=event["type"],
                            object=UpdateObject(
                                message=UpdateMessage(
                                    from_id=msg["from_id"],
                                    text=msg["text"],
                                    id=msg["id"]
                                )
                            )
                        ))
                
                if updates:
                    await self.app.store.bots_manager.handle_updates(updates)
        
        except Exception as e:
            self.logger.error(f"Poll error: {e}")
            await self._get_long_poll_service()


    async def send_message(self, message: Message) -> None:
            params = {
                "user_id": message.user_id,
                "message": message.text,
                "random_id": 0,
                "access_token": self.app.config.bot.token,
            }
            url = self._build_query("https://api.vk.com", "messages.send", params)
            
            async with self.session.get(url) as resp:
                data = await resp.json()
                if "error" in data:
                    self.logger.error(f"Failed to send message: {data}")
