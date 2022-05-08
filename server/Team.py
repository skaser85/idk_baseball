import os
from dataclasses import dataclass, field
from DBHandler import DBHandler
from TeamColor import TeamColor
from Player import Player

DB_FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'idk_db.db'))

@dataclass
class Team:
    id: int
    city: str = ""
    name: str = ""
    short_name: str = ""
    league: str = ""
    division: str = ""
    full_team_name: str = ""

    def __post_init__(self):
        if self.id == 0:
            return
        with DBHandler(DB_FILEPATH) as db:
            team = db.fetch_one('SELECT * FROM Team WHERE ID=?', (self.id,))
            self.city = team[1]
            self.name = team[2]
            self.short_name = team[3]
            self.league = team[4]
            self.division = team[5]
            self.full_team_name = team[6]

    def create_team_dict(self) -> dict:
        return {
            'id': self.id,
            'city': self.city,
            'name': self.name,
            'shortName': self.short_name,
            'league': self.league,
            'division': self.division,
            'fullTeamName': self.full_team_name,
        }

    def create_team_data(self) -> dict:
        teamData = {}
        with DBHandler(DB_FILEPATH) as db:
            team = db.fetch_one(f'SELECT * FROM Team WHERE ID = {self.id}')
            colors = [TeamColor(c[0]).create_color_dict() for c in db.fetch_all(f'SELECT * FROM "Team Color" WHERE "Team ID" = {self.id}')]
            teamData = self.create_team_dict()
            teamData['colors'] = colors
        return teamData

    def create_lineup_data(self, game_id: int) -> dict:
        with DBHandler(DB_FILEPATH) as db:
            lineup = db.fetch_all(f"""
                SELECT * 
                FROM Lineup
                WHERE
                    "Game ID"=? AND
                    "Team ID"=? AND
                    Active=?
            """, (game_id, self.id, True))
            lineup_data = {}
            for line in lineup:
                lineup_data[line[2]] = Player(line[3]).create_player_dict()
            return lineup_data

    def create_batting_order_data(self) -> dict:
        batting_order_data = {}
        with DBHandler(DB_FILEPATH) as db:
            players = [Player(p[0]) for p in db.fetch_all(f'SELECT * FROM Player WHERE "Team ID" = {self.id}')]
            pitchers = [p for p in players if p.position.upper() in ['SP','RP']]
            pitcher_IDs = [p.id for p in pitchers]
            position_players = [p for p in players if not p.id in pitcher_IDs]
            pos_players_batting = [Player(p.id).batting_order_text for p in position_players]
            pitchers_batting = [Player(p.id).batting_order_text for p in pitchers]
            batting_order_data = {
                'players': [p.create_player_dict() for p in players],
                'pitchers': [p.create_player_dict() for p in pitchers],
                'position_players': [p.create_player_dict() for p in position_players],
                'batting_order_data': {
                    'Position Players': pos_players_batting,
                    'Pitchers': pitchers_batting
                }
            }
        return batting_order_data

    def create_team_game_data(self, game_id: int) -> dict:
        team_data = {}
        if self.id > 0:
            team_data = self.create_team_data()
            team_data['lineup'] = self.create_lineup_data(game_id)
            team_data['battingOrderData'] = self.create_batting_order_data()
        return team_data
