from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from app.admin.models import Admin
from app.store import Store, setup_store
from app.store.database.database import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet
import base64

class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database = Database()

class Request(AiohttpRequest):
    admin: Admin | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})





def setup_app(config_path: str) -> Application:
    app = Application()
    

    setup_logging(app)
    setup_config(app, config_path)
    app.database = Database()
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup_session(
        app,
        EncryptedCookieStorage(
            secret_key,
            cookie_name=app.config.session.cookie_name,
            max_age=app.config.session.lifetime,
            httponly=app.config.session.http_only,
            secure=app.config.session.secure
        )
    )
    

    setup_aiohttp_apispec(app, title='pupupu Application', swagger_path='/docs')
    setup_store(app)
    setup_middlewares(app)
    setup_routes(app)
    
    return app
