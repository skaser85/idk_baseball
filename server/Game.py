import os
from dataclasses import dataclass, field
from DBHandler import DBHandler
from Team import Team
from Player import Player

DB_FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'idk_db.db'))

@dataclass
class Game:
    id: int
    home_team_id: int = 0
    away_team_id: int = 0
    home_score: int = 0
    away_score: int = 0
    pitcher_id: int = 0
    batter_id: int = 0
    first_base_occupied: bool = False
    second_base_occupied: bool = False
    third_base_occupied: bool = False
    top_of_inning: bool = True
    inning_no: int = 0
    outs: int = 0
    balls: int = 0
    strikes: int = 0
    pitches: int = 0
    batting_avg: int = 0

    def __post_init__(self):
        with DBHandler(DB_FILEPATH) as db:
            game = db.fetch_one('SELECT * FROM Game WHERE ID=?', (self.id,))
            self.home_team_id = game[1]
            self.away_team_id = game[2]
            self.home_score = game[3]
            self.away_score = game[4]
            self.pitcher_id = game[5]
            self.batter_id = game[6]
            self.first_base_occupied = game[7]
            self.second_base_occupied = game[8]
            self.third_base_occupied = game[9]
            self.top_of_inning = game[10]
            self.inning_no = game[11]
            self.outs = game[12]
            self.balls = game[13]
            self.strikes = game[14]
            self.pitches = game[15]
            self.batting_avg = game[16]

    def create_game_data_dict(self) -> dict:
        return {
            'id': self.id,
            'homeTeam': Team(self.home_team_id).create_team_game_data(self.id),
            'awayTeam': Team(self.away_team_id).create_team_game_data(self.id),
            'homeScore': self.home_score,
            'awayScore': self.away_score,
            'pitcher': Player(self.pitcher_id).create_player_dict(),
            'batter': Player(self.batter_id).create_player_dict(),
            'firstBaseOccupied': self.first_base_occupied,
            'secondBaseOccupied': self.second_base_occupied,
            'thirdBaseOccupied': self.third_base_occupied,
            'topOfInning': self.top_of_inning,
            'inningNo': self.inning_no,
            'outs': self.outs,
            'balls': self.balls,
            'strikes': self.strikes,
            'pitches': self.pitches,
            'battingAvg': self.batting_avg,
        }

    def get_batting_order(self, team_id: int) -> dict:
        if self.home_team_id == team_id:
            return Team(self.home_team_id).create_batting_order_data()
        elif self.away_team_id == team_id:
            return Team(self.away_team_id).create_batting_order_data()
        else:
            return {}

    def add_player_to_lineup(self, team_id: int, player_data: dict) -> None:
        with DBHandler(DB_FILEPATH) as db:
            player_id = player_data['playerID']
            order_no = player_data['orderNo']
            is_pitcher = player_data['isPitcher'] == True
            sql = """
                SELECT * 
                FROM Lineup 
                WHERE 
                    "Game ID"=? AND 
                    "Team ID"=? AND
                    "Order No."=? AND
                    "Is Pitcher"=?
            """

            exists = db.fetch_one(sql, (self.id, team_id, order_no, is_pitcher))

            if exists is None:
                db.insert(f"""
                    INSERT 
                    INTO Lineup
                        (
                            "Game ID",
                            "Team ID",
                            "Order No.",
                            "Player ID",
                            "Is Pitcher"
                        )
                    VALUES
                        (?,?,?,?,?);
                """, (self.id, team_id, order_no, player_id, is_pitcher))
            else:
                db.update(f"""
                    UPDATE Lineup 
                    SET 
                        "Player ID"=?
                    WHERE 
                        "Game ID"=? AND
                        "Team ID"=? AND
                        "Order No."=?
                    """,
                    (player_id, self.id, team_id, order_no)
                )

            if is_pitcher:
                if self.pitcher_id == 0:
                    if self.top_of_inning == 1:
                        if self.home_team_id == int(team_id):
                            db.update(f"""
                                UPDATE Game
                                SET
                                    "Pitcher ID"=?
                                WHERE
                                    ID=?
                            """,(player_id, self.id))
                    else:
                        if self.away_team_id == team_id:
                            db.update(f"""
                                UPDATE Game
                                SET
                                    "Pitcher ID"=?
                                WHERE
                                    ID=?
                            """,(player_id, self.id))
            else:
                if self.batter_id == 0:
                    if self.top_of_inning == 1:
                        if self.away_team_id == int(team_id):
                            db.update(f"""
                                UPDATE Game
                                SET
                                    "Batter ID"=?
                                WHERE
                                    ID=?
                            """,(player_id, self.id))
                    else:
                        if self.home_team_id == int(team_id):
                            db.update(f"""
                                UPDATE Game
                                SET
                                    "Batter ID"=?
                                WHERE
                                    ID=?
                            """,(player_id, self.id))