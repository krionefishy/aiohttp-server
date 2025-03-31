import typing
from dataclasses import dataclass
from datetime import datetime
import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application

@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class SessionConfig:
    key: str
    lifetime: int = 24*3600
    cookie_name: str = "session_id"
    http_only: bool = True
    secure: bool = False
    

@dataclass
class AdminConfig:
    id: int
    email: str
    password: str


@dataclass
class BotConfig:
    token: str
    group_id: int


@dataclass
class Config:
    admin: AdminConfig
    database: DatabaseConfig
    session: SessionConfig | None = None
    bot: BotConfig | None = None


def setup_config(app: "Application", config_path: str):
    # TODO: добавить BotConfig и SessionConfig по данным из config.yml
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)


    app.config = Config(
        admin=AdminConfig(
            id=1,
            email=raw_config["admin"]["email"],
            password=raw_config["admin"]["password"],
        ),
        database=DatabaseConfig(
            host=raw_config["database"]["host"],
            port=raw_config["database"]["port"],
            user=raw_config["database"]["user"],
            password=raw_config["database"]["password"],
            database=raw_config["database"]["database"],
        ),
        session=SessionConfig(
            key=raw_config["session"]["key"],
            lifetime=raw_config["session"].get("lifetime", 86400), 
            cookie_name=raw_config["session"].get("cookie_name", "session_id"),
            http_only=raw_config["session"].get("http_only", True),
            secure=raw_config["session"].get("secure", False)
        ),
        bot=BotConfig(
            token=raw_config["bot"]["token"],
            group_id=raw_config["bot"]["group_id"]
        )
    )
    