import os
from urllib import response
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from DBHandler import DBHandler

app = Flask(__name__)
api = Api(app)
CORS(app)

DB_FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'idk_db.db'))

def get_teams() -> list:
    teams = []
    with DBHandler(DB_FILEPATH) as db:
        teams = db.fetch_all(f'SELECT * FROM Team')
        teams = [create_team_dict(team) for team in teams]
    return teams

def create_color_dict(colors: tuple) -> dict:
    return {
        'name': colors[2],
        'hex': colors[3] if len(colors[3]) == 6 else colors[3].zfill(6),
        'r': colors[4],
        'g': colors[5],
        'b': colors[6],
        'isPrimary': colors[7]
    }

def create_team_dict(team: tuple) -> dict:
    return {
        'id': team[0],
        'city': team[1],
        'name': team[2],
        'shortName': team[3],
        'league': team[4],
        'division': team[5],
        'fullTeamName': team[6],
    }

def create_team_data(team_id: int) -> dict:
    teamData = {}
    if team_id > 0:
        with DBHandler(DB_FILEPATH) as db:
            team = db.fetch_one(f'SELECT * FROM Team WHERE ID = {team_id}')
            colors = [create_color_dict(c) for c in db.fetch_all(f'SELECT * FROM "Team Color" WHERE "Team ID" = {team_id}')]
            teamData = create_team_dict(team)
            teamData['colors'] = colors
    return teamData

def create_batting_order_text(player_id: int, full_name: str, position: str) -> str:
    return f'{player_id} - {full_name}, {position}'

def create_player_dict(player: tuple) -> dict:
    return {
        'id': player[0],
        'firstName': player[1],
        'lastName': player[2],
        'fullName': f'{player[1]} {player[2]}',
        'team': create_team_data(player[3]),
        'position': player[4],
        'bats': player[5],
        'throws': player[6],
        'age': player[7],
        'weight_lbs': player[8],
        'birthPlace': player[9],
        'jerseyNo': player[10],
        'height': f'{player[11]} ft. {player[12]} in.',
        'batting_order_text': create_batting_order_text(player[0],f'{player[1]} {player[2]}',player[4])
    }

def create_lineup_data(game_id: int, team_id: int) -> dict:
    with DBHandler(DB_FILEPATH) as db:
        lineup = db.fetch_all(f"""
            SELECT * 
            FROM Lineup
            WHERE
                "Game ID"=? AND
                "Team ID"=?
        """, (game_id, team_id))
        lineup_data = {}
        for line in lineup:
            player = db.fetch_one('SELECT * FROM Player WHERE ID=?', (line[3],))
            lineup_data[line[2]] = create_player_dict(player)
        return lineup_data

def create_game_data_dict(game_id: int) -> dict:
    with DBHandler(DB_FILEPATH) as db:
        game = db.fetch_one(f'SELECT * FROM Game WHERE ID = {game_id}')
        
        homeTeamData = {}
        if game[1] > 0:
            homeTeamData = create_team_data(game[1])
            homeTeamData['lineup'] = create_lineup_data(game_id, game[1])
            homeTeamData['battingOrderData'] = create_batting_order_data(game[1])
        
        awayTeamData = {}
        if game[2] > 0:
            awayTeamData = create_team_data(game[2])
            awayTeamData['lineup'] = create_lineup_data(game_id, game[2])
            awayTeamData['battingOrderData'] = create_batting_order_data(game[2])
        
        pitcherData = {}
        if game[5] > 0:
            pitcher = db.fetch_one(f'SELECT * FROM Player WHERE ID = {game[5]}')
            pitcherData = create_player_dict(pitcher)

        batterData = {}
        if game[6] > 0:
            batter = db.fetch_one(f'SELECT * FROM Player WHERE ID = {game[6]}')
            batterData = create_player_dict(batter)

        return {
            'id': game[0],
            'homeTeam': homeTeamData,
            'awayTeam': awayTeamData,
            'homeScore': game[3],
            'awayScore': game[4],
            'pitcher': pitcherData,
            'batter': batterData,
            'firstBaseOccupied': False if game[7] == 0 else True,
            'secondBaseOccupied': False if game[8] == 0 else True,
            'thirdBaseOccupied': False if game[9] == 0 else True,
            'topOfInning': False if game[10] == 0 else True,
            'inningNo': game[11],
            'outs': game[12],
            'balls': game[13],
            'strikes': game[14],
            'pitches': game[15],
            'battingAvg': game[16],
        }

def create_batting_order_data(team_id: int) -> dict:
    batting_order_data = {}
    with DBHandler(DB_FILEPATH) as db:
        players = [create_player_dict(p) for p in db.fetch_all(f'SELECT * FROM Player WHERE "Team ID" = {team_id}')]
        pitchers = [p for p in players if p['position'].upper() in ['SP','RP']]
        pitcher_IDs = [p['id'] for p in pitchers]
        position_players = [p for p in players if not p['id'] in pitcher_IDs]
        pos_players_batting = [f'{create_batting_order_text(p["id"],p["fullName"],p["position"])}' for p in position_players]
        pitchers_batting = [f'{create_batting_order_text(p["id"],p["fullName"],p["position"])}' for p in pitchers]
        batting_order_data = {
            'players': players,
            'pitchers': pitchers,
            'position_players': position_players,
            'batting_order_data': {
                'Position Players': pos_players_batting,
                'Pitchers': pitchers_batting
            }
        }
    return batting_order_data

def get_teams_in_leagues_and_divisions(teams: list) -> list:        
    teams_in_leagues_and_divisions = {
        'AL Central': [],
        'AL East': [],
        'AL West': [],
        'NL Central': [],
        'NL East': [],
        'NL West': []
    }
    
    for team in teams:
        league = 'AL' if team['league'] == 'American' else 'NL'
        league_div = f'{league} {team["division"]}'
        teams_in_leagues_and_divisions[league_div].append(team['fullTeamName'])

    return teams_in_leagues_and_divisions

class CreateGame(Resource):
    def get(self):
        with DBHandler(DB_FILEPATH) as db:
            db.insert(f'INSERT INTO Game (ID) VALUES (null);')
            game_no = db.cursor.lastrowid
            
            return {
                'game_data': create_game_data_dict(game_no)
            }, 201

class GetTeams(Resource):
    def get(self):
        return {'teams': get_teams()}, 201

class GetGames(Resource):
    def get(self):
        with DBHandler(DB_FILEPATH) as db:
            games = db.fetch_all('SELECT ID FROM Game')
        return {'games': [g[0] for g in games]}, 201

class GetGame(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('gameID')
        args = parser.parse_args()
        return {
                'game_data': create_game_data_dict(args.gameID)
            }, 201

class AddTeam(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('teamName')
        parser.add_argument('gameID')
        parser.add_argument('side') # Home or Away
        args = parser.parse_args()
        
        with DBHandler(DB_FILEPATH) as db:
            team_data = db.fetch_one(f'SELECT ID FROM Team WHERE "Full Team Name" = "{args.teamName}"')
            
            if team_data is None:
                return {
                    'game_data': create_game_data_dict(args.gameID)
                }, 201
            
            team_id = team_data[0]
            
            db.update(f'UPDATE Game SET "{args.side} Team ID"=? WHERE ID=?', (team_id, args.gameID))

            return {
                'game_data': create_game_data_dict(args.gameID)
            }, 201

class GetPlayers(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('teamID')
        args = parser.parse_args()
        print(args.teamID)
        batting_order_data = create_batting_order_data(args.teamID)
        print(batting_order_data)
        return {'batting_order_data': batting_order_data}, 201

class AddPlayerToLineup(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('gameID')
        parser.add_argument('teamID')
        parser.add_argument('playerID')
        parser.add_argument('orderNo')
        args = parser.parse_args()
        with DBHandler(DB_FILEPATH) as db:
            sql = f"""
                SELECT * 
                FROM Lineup 
                WHERE 
                    "Game ID" = {args.gameID} AND 
                    "Team ID" = {args.teamID} AND
                    "Order No." = {args.orderNo}
            """

            exists = db.fetch_one(sql)

            if exists is None:
                db.insert(f"""
                    INSERT 
                    INTO Lineup
                        (
                            "Game ID",
                            "Team ID",
                            "Order No.",
                            "Player ID"
                        )
                    VALUES
                        (
                            {args.gameID},
                            {args.teamID},
                            {args.orderNo},
                            {args.playerID}
                        );
                """)
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
                    (args.playerID, args.gameID, args.teamID, args.orderNo)
                )
        return {}, 201

class GetTeamsForTeamSelect(Resource):
    def get(self):
        teams = get_teams()
        return {
            'teams': teams,
            'teamsLeaguesDivs': get_teams_in_leagues_and_divisions(teams)
        }, 201

api.add_resource(CreateGame, '/creategame')
api.add_resource(GetTeams, '/getteams')
api.add_resource(AddTeam, '/addteam')
api.add_resource(GetPlayers, '/getplayers')
api.add_resource(AddPlayerToLineup, '/addplayertolineup')
api.add_resource(GetGames, '/getgames')
api.add_resource(GetGame, '/getgame')
api.add_resource(GetTeamsForTeamSelect, '/getteamsforteamselect')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)
    # app.run(debug=True, port=8008)