import os
from urllib import response
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from db import DB

app = Flask(__name__)
api = Api(app)
CORS(app)

DB_FILEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'idk_db.db'))

# parser = reqparse.RequestParser()
# parser.add_argument('string')
# parser.add_argument('scale')
# parser.add_argument('png_filepath')

# class JP2D(Resource):
#     def post(self):
#         args = parser.parse_args()
#         qr = pyqrcode.create(args['string'])
#         qr.png(args['png_filepath'], scale=args['scale'])
#         b64 = qr.png_as_base64_str()
#         return {'b64': b64}, 201

class CreateGame(Resource):
    @staticmethod
    def create_team_dict(team: tuple) -> dict:
        return {
            'id': team[0],
            'city': team[1],
            'name': team[2],
            'shortName': team[3],
            'league': team[4],
            'division': team[5],
            'fullTeamName': team[6]
        }

    def get(self):
        db = DB(DB_FILEPATH)
        teams = db.fetch_all(f'SELECT * FROM Team')
        teams = [self.create_team_dict(team) for team in teams]
        db.insert(f'INSERT INTO Game (ID) VALUES (null);')
        game_no = db.cursor.lastrowid
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
        db.cursor.close()
        db.connection.close()
        return {
            'game_no': game_no,
            'teams': teams,
            'teams_in_leagues_and_divisions': teams_in_leagues_and_divisions
        }, 201

class GetTeams(Resource):
    def get(self):
        db = DB(DB_FILEPATH)
        teams = db.fetch_all(f'SELECT * FROM Team')
        teams = [[t for t in team] for team in teams]
        db.cursor.close()
        db.connection.close()
        return {'teams': teams}, 201

class GetTeamData(Resource):
    @staticmethod
    def create_color_dict(colors: tuple) -> dict:
        return {
            'name': colors[2],
            'hex': colors[3] if len(colors[3]) == 6 else colors[3].zfill(6),
            'r': colors[4],
            'g': colors[5],
            'b': colors[6],
            'isPrimary': colors[7]
        }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('teamName')
        args = parser.parse_args()
        db = DB(DB_FILEPATH)
        
        team_data = db.fetch_one(f'SELECT ID, "Short Name" FROM Team WHERE "Full Team Name" = "{args.teamName}"')
        if team_data is None:
            return {}, 201
        team_id = team_data[0]
        short_name = team_data[1]

        colors = db.fetch_all(f'SELECT * FROM "Team Color" WHERE "Team ID" = {team_id}')
        
        db.cursor.close()
        db.connection.close()
        return {
            'team_id': team_id,
            'short_name': short_name,
            'colors': [self.create_color_dict(c) for c in colors]
        }, 201

api.add_resource(CreateGame, '/creategame')
api.add_resource(GetTeams, '/getteams')
api.add_resource(GetTeamData, '/getteamdata')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)
    # app.run(debug=True, port=8008)