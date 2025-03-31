import typing
from logging import getLogger

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app
        self.logger = getLogger("accessor")

        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: "Application"):
        self.logger.info(f"Connecting {self.__class__.__name__}")
        try:
            await self._on_connect()
            self.logger.info(f"Successfully connected {self.__class__.__name__}")
        except Exception as e:
            self.logger.error(f"Connection failed in {self.__class__.__name__}: {e}")
            raise

    async def disconnect(self, app: "Application"):
        self.logger.info(f"Disconnecting {self.__class__.__name__}")
        try:
            await self._on_disconnect()
            self.logger.info(f"Successfully disconnected {self.__class__.__name__}")
        except Exception as e:
            self.logger.error(f"Disconnection error in {self.__class__.__name__}: {e}")
            raise


    async def _on_connect(self):
        pass

    async def _on_disconnect(self):
        pass
