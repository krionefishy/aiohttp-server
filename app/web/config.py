import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    pass


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

    """app.config = Config(
        admin=AdminConfig(
            email=raw_config["admin"]["email"],
            password=raw_config["admin"]["password"],
        ),
        session=SessionConfig(
            key=raw_config["session"]["key"],
        ),
        bot=BotConfig(
            token=raw_config["bot"]["token"],
            group_id=raw_config["bot"]["group_id"],
        ),
    )"""

    app.config = Config(
        admin=AdminConfig(
            id=1,
            email=raw_config["admin"]["email"],
            password=raw_config["admin"]["password"],
        ),
    )
