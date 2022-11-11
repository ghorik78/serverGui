from utils.constants import *

import typing
import dataclasses

PLAYER_CUSTOM_FIELDS = ['control_obj', 'role_obj']  # combo box will be created for these fields


@dataclasses.dataclass
class PlayerParams:
    # Add new alias if you need to fill combo box by values from utils.constants
    aliases = dict(control_obj=CONTROL_OBJECTS,
                   role_obj=ROLES)

    name_player: str = "not set"
    control_obj: str = ""
    role_obj: str = ""
    method_control_obj: str = ""
    ip: str = "127.0.0.1"
    port: int = 0


@dataclasses.dataclass
class TeamParams:
    players: typing.List[PlayerParams]
    name_team: str = "not set"
    color_team: list = (0, 0, 0)


@dataclasses.dataclass
class Game:
    teams: typing.List[TeamParams]


OBJECT_CUSTOM_FIELDS = []


@dataclasses.dataclass
class ObjectParams:
    aliases = dict()

    role: str = "role not set"
    position: list = (0, 0, 0)
    ind_for_led_controller: int = 0
    custom_settings: str = ""
    game_mechanics: int = 0
    filter: list = ""


@dataclasses.dataclass
class PolygonParams:
    objects: typing.List[ObjectParams]


@dataclasses.dataclass
class Config:
    game: Game
    polygon: PolygonParams
