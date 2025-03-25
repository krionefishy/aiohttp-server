import typing
from dataclasses import dataclass
from datetime import datetime
import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


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
    pass


@dataclass
class Config:
    admin: AdminConfig
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
        session=SessionConfig(
            key=raw_config["session"]["key"],
            lifetime=raw_config["session"].get("lifetime", 86400),  # 1 день по умолчанию
            cookie_name=raw_config["session"].get("cookie_name", "session_id"),
            http_only=raw_config["session"].get("http_only", True),
            secure=raw_config["session"].get("secure", False)
        )
    )
    