import os
from dataclasses import dataclass, field
from DBHandler import DBHandler

DB_FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'idk_db.db'))

@dataclass
class Player:
    id: int
    first_name: str = ""
    last_name: str = ""
    team_id: int = 0
    position: str = ""
    bats: str = ""
    throws: str = ""
    age: int = 0
    weight_lbs: int = 0
    birth_place: str = ""
    jersey_no: int = 0
    height_ft: int = 0
    height_in: int = 0
    full_name: str = ""
    height: str = ""
    batting_order_text: str = ""

    def __post_init__(self):
        if self.id == 0:
            return
        with DBHandler(DB_FILEPATH) as db:
            player = db.fetch_one('SELECT * FROM Player WHERE ID=?', (self.id,))
            self.first_name = player[1]
            self.last_name = player[2]
            self.team_id = player[3]
            self.position = player[4]
            self.bats = player[5]
            self.throws = player[6]
            self.age = player[7]
            self.weight_lbs = player[8]
            self.birth_place = player[9]
            self.jersey_no = player[10]
            self.height_ft = player[11]
            self.height_in = player[12]
            self.full_name = f'{self.first_name} {self.last_name}'
            self.height = f'{self.height_ft} ft. {self.height_in} in.',
            self.batting_order_text = f'{self.id} - {self.full_name}, {self.position}'

    def create_player_dict(self) -> dict:
        if self.id == 0:
            return {}
        else:
            return {
                'id': self.id,
                'firstName': self.first_name,
                'lastName': self.last_name,
                'fullName': self.full_name,
                # 'team': create_team_data(player[3]),
                'position': self.position,
                'bats': self.bats,
                'throws': self.throws,
                'age': self.age,
                'weight_lbs': self.weight_lbs,
                'birthPlace': self.birth_place,
                'jerseyNo': self.jersey_no,
                'height': self.height,
                'batting_order_text': self.batting_order_text
            }
