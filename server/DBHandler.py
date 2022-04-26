from db import DB

class DBHandler:
    def __init__(self, db_filepath: str):
        self.db = DB(db_filepath)

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.cursor.close()
        self.db.connection.close()

if __name__ == '__main__':
    with DBHandler('idk_db.db') as db:
        teams = db.fetch_all('SELECT * FROM Team')
        print(teams)
