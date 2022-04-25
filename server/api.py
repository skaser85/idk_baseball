import os
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
            'division': team[5]
        }

    def get(self):
        db = DB(DB_FILEPATH)
        teams = db.fetch_all(f'SELECT * FROM Team')
        teams = [self.create_team_dict(team) for team in teams]
        db.insert(f'INSERT INTO Game (ID) VALUES (null);')
        game_no = db.cursor.lastrowid
        db.cursor.close()
        db.connection.close()
        return {'game_no': game_no, 'teams': teams}, 201

class GetTeams(Resource):
    def get(self):
        db = DB(DB_FILEPATH)
        teams = db.fetch_all(f'SELECT * FROM Team')
        teams = [[t for t in team] for team in teams]
        db.cursor.close()
        db.connection.close()
        return {'teams': teams}, 201

api.add_resource(CreateGame, '/creategame')
api.add_resource(GetTeams, '/getteams')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008, debug=True)
    # app.run(debug=True, port=8008)