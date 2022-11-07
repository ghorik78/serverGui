import typing

import json
import dataclasses


@dataclasses.dataclass
class PlayerParams:
    name_player: str = "name player not set"
    control_obj: str = ""
    role_obj: str = ""
    method_control_obj: str = ""
    ip: str = "127.0.0.1"
    port: int = 0


@dataclasses.dataclass
class TeamParams:
    players: typing.List[PlayerParams]
    name_team: str = "team name not set"
    color_team: list = (0, 0, 0)


@dataclasses.dataclass
class Game:
    teams: typing.List[TeamParams]