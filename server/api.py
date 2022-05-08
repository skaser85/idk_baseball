import os
from urllib import response
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from json import dumps, loads
from DBHandler import DBHandler
from Game import Game
from Team import Team

app = Flask(__name__)
api = Api(app)
CORS(app)

DB_FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'idk_db.db'))

def get_teams() -> list:
    teams = []
    with DBHandler(DB_FILEPATH) as db:
        teams = db.fetch_all(f'SELECT * FROM Team')
        teams = [Team(team[0]).create_team_dict() for team in teams]
    return teams

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
                'game_data': Game(game_no).create_game_data_dict()
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
                'game_data': Game(args.gameID).create_game_data_dict()
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
                    'game_data': Game(args.gameID).create_game_data_dict()
                }, 201
            
            team_id = team_data[0]
            
            db.update(f'UPDATE Game SET "{args.side} Team ID"=? WHERE ID=?', (team_id, args.gameID))

            return {
                'game_data': Game(args.gameID).create_game_data_dict()
            }, 201

class GetPlayers(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('gameID')
        parser.add_argument('teamID')
        args = parser.parse_args()
        batting_order_data = Game(args.gameID).get_batting_order(args.teamID)
        return {'batting_order_data': batting_order_data}, 201

class SaveLineup(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('gameID')
        parser.add_argument('teamID')
        parser.add_argument('lineup')
        args = parser.parse_args()
        game = Game(args.gameID)
        lineup = loads(args.lineup)
        for player in lineup:
            if len(player) > 0:
                game.add_player_to_lineup(args.teamID, player)
        return {'game_data': Game(args.gameID).create_game_data_dict()}, 201

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
api.add_resource(SaveLineup, '/savelineup')
api.add_resource(GetGames, '/getgames')
api.add_resource(GetGame, '/getgame')
api.add_resource(GetTeamsForTeamSelect, '/getteamsforteamselect')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)
    # app.run(debug=True, port=8008)