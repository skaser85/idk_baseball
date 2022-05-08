import os
from dataclasses import dataclass, field
from DBHandler import DBHandler

DB_FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'idk_db.db'))

@dataclass
class Lineup:
    game_id: int
    team_id: int
    order_no: int
    active: bool
    player_id: int = 0
    is_pitcher: bool = False

    def __post_init__(self):
        with DBHandler(DB_FILEPATH) as db:
            lineup = db.fetch_one("""
                SELECT *
                FROM Lineup
                WHERE 
                    "Game ID"=? AND
                    "Team ID"=? AND
                    "Order No."=? AND
                    Active=?
                """, (self.game_id, self.team_id, self.order_no, self.active))

            