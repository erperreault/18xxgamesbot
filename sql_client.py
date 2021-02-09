import sqlite3

def make_user_table(cursor: object):
    cursor.execute('CREATE TABLE IF NOT EXISTS users (web_name text, web_id text unique, discord_id text unique)')

def insert_user(cursor: object, web_name: str, web_id: str, discord_id: str):
    cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (web_name, web_id, discord_id))

def select_user(cursor: object, discord_id: str) -> list:
    return cursor.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,)).fetchone()

def update_user(cursor: object, discord_id: str, new_name: str):
    cursor.execute('UPDATE users SET web_name = ? WHERE web_name = ?', (new_name, discord_id))

def make_games_table(cursor: object):
    cursor.execute('CREATE TABLE IF NOT EXISTS games (game_id text, channel text, acting_player text)')

def insert_game(cursor: object, game_id: str, channel: str, acting_player: str):
    cursor.execute('INSERT INTO games VALUES (?, ?, ?)', (game_id, channel, acting_player))

def select_game(cursor: object, game_id: str) -> list:
    return cursor.execute('SELECT * FROM games WHERE game_id = ?', (game_id,)).fetchone()

def update_acting_player(cursor: object, game_id, acting_player: str):
    cursor.execute('UPDATE games SET acting_player = ? WHERE game_id = ?', (acting_player, game_id))