from dataclasses import dataclass, field
from sqlite3 import connect, Cursor, Connection

@dataclass
class DB:
    db_file: str
    connection: Connection = field(init=False)
    cursor: Cursor = field(init=False)

    def __post_init__(self):
        self.connection = connect(self.db_file)
        self.cursor = self.connection.cursor()

    def fetch_one(self, sql: str, values: tuple = ()) -> Cursor:
        return self.cursor.execute(sql, values).fetchone()
    
    def fetch_all(self, sql: str, values: tuple = ()) -> Cursor:
        return self.cursor.execute(sql, values).fetchall()

    def insert(self, sql: str, values: tuple[str] = ()):
        self.cursor.execute(sql, values)
        self.connection.commit()

    def update(self, sql: str, values: tuple[str] = ()):
        self.cursor.execute(sql, values)
        self.connection.commit()

if __name__ == '__main__':
    db = DB('idk_db.db')
    # teams = db.fetch_all(f'SELECT * FROM Team')
    # print(teams)
    # db.insert(f'INSERT INTO Game (ID) VALUES (null);')
    # print(db.cursor.lastrowid)
    home_team_id = 1
    game_id = 143
    db.update(f'UPDATE Game SET "Home Team ID"=? WHERE ID=?', (home_team_id, game_id))
    db.cursor.close()
    db.connection.close()