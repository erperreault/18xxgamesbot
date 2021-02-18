import psycopg2

def connect(db_fp):
    return psycopg2.connect(db_fp, sslmode='require')

def execute_query(connection, query, args=()):
    cursor = connection.cursor()
    try:
        cursor.execute(query, args)
        connection.commit()
    except Exception as e:
        print(f'{query} // Error: {e}')

def read_query(connection, query, args=()):
    cursor = connection.cursor()
    try:
        cursor.execute(query, args)
        return cursor.fetchall()
    except Exception as e:
        print(f'{query} // Error: {e}')

def make_user_table(connection: object):
    execute_query(connection, 'CREATE TABLE IF NOT EXISTS users (web_name text, web_id text unique, discord_id text unique)')

def insert_user(connection: object, web_name: str, web_id: str, discord_id: str):
    execute_query(connection, 'INSERT INTO users VALUES (?, ?, ?)', (web_name, web_id, discord_id))

def select_user(connection: object, discord_id: str) -> list:
    return read_query(connection, 'SELECT * FROM users WHERE discord_id = ?', (discord_id,))

def select_user_by_web_id(connection: object, web_id: str) -> list:
    return read_query(connection, 'SELECT * FROM users WHERE web_id = ?', (web_id,))

def update_user(connection: object, discord_id: str, new_name: str):
    execute_query(connection, 'UPDATE users SET web_name = ? WHERE discord_id = ?', (new_name, discord_id))

def make_games_table(connection: object):
    execute_query(connection, 'CREATE TABLE IF NOT EXISTS games (game_id text unique, channel text, acting_player text)')

def insert_game(connection: object, game_id: str, channel: str, acting_player: str):
    execute_query(connection, 'INSERT INTO games VALUES (?, ?, ?)', (game_id, channel, acting_player))

def select_game(connection: object, game_id: str) -> list:
    return read_query(connection, 'SELECT * FROM games WHERE game_id = ?', (game_id,))

def update_acting_player(connection: object, game_id, acting_player: str):
    execute_query(connection, 'UPDATE games SET acting_player = ? WHERE game_id = ?', (acting_player, game_id))

def update_game_channel(connection: object, channel_id: str, game_id: str):
    execute_query(connection, 'UPDATE games SET channel = ? WHERE game_id = ?', (channel_id, game_id))

def delete_game(connection: object, game_id: str):
    execute_query(connection, 'DELETE FROM games WHERE game_id = ?', (game_id,))