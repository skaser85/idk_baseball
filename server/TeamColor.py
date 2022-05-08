import os
from dataclasses import dataclass, field
from DBHandler import DBHandler

DB_FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'idk_db.db'))

@dataclass
class TeamColor:
    id: int
    team_id: int = 0
    color_name: str = ""
    hex_value: str = ""
    r: int = 0
    g: int = 0
    b: int = 0
    is_primary: bool = False

    def __post_init__(self):
        with DBHandler(DB_FILEPATH) as db:
            color = db.fetch_one('SELECT * FROM "Team Color" WHERE ID=?', (self.id,))
            self.team_id = color[1]
            self.color_name = color[2]
            self.hex_value = color[3].zfill(6)
            self.r = color[4]
            self.g = color[5]
            self.b = color[6]
            self.is_primary = color[7]

    def create_color_dict(self) -> dict:
        return {
            'name': self.color_name,
            'hex': self.hex_value,
            'r': self.r,
            'g': self.g,
            'b': self.b,
            'isPrimary': self.is_primary
        }
