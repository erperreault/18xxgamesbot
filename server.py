#!/usr/bin/env python3

import os, json, urllib.request, discord, re, asyncio, sql_client, sqlite3, verbage, dotenv
from dotenv import load_dotenv

### Constants ###
client = discord.Client()
help_command = '!help'
track_command = '!track'
startup_command = '!startup'
sync_command = '!sync'
unsync_command = '!unsync'
users_db_fp = '.users.db'
games_db_fp = '.games.db'

### Discord Events ###

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}.')
    await auto_checker()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif str(message.channel.type) == 'text':

        if message.content.startswith(track_command):
            await track_game(message)

        elif message.content.startswith(sync_command):
            await sync_player_id(message)

        elif message.content.startswith(unsync_command):
            await unsync_player_id(message)

        elif message.content.startswith(help_command):
            await bot_help(message)

    elif str(message.channel.type) == 'private':

        if not message.content.startswith('!'):
            await message.channel.send(f'Hello! Say "{help_command}" if you need help.')

        elif message.content.startswith(help_command):
            await bot_help(message)

        else:
            await message.channel.send(
                f'Sorry, I don\'t know that command. Say "{help_command}" for the commands I do know.')

### Interior Life Of Bot ###

def setup_users_db(users_db_fp):
    conn = sqlite3.connect(users_db_fp)

    sql_client.make_user_table(conn)

    conn.close()
    
def setup_games_db(game_db_fp):
    conn = sqlite3.connect(games_db_fp)

    sql_client.make_games_table(conn)

    conn.close()

def get_player_mention(web_id):
    conn = sql_client.connect(users_db_fp)
    player = sql_client.select_user_by_web_id(conn, web_id)[0]
    web_name = player[0]
    discord_id = player[2]
    if not discord_id:
        return web_name 
    else:
        return f'<@{discord_id}>'
    conn.close()

def fetch_game_data(id: str) -> str:
    with urllib.request.urlopen(f'https://18xx.games/api/game/{id}') as response:
        return json.loads(response.read())

def game_id_regex(message):
    '''Finds the channel ID.'''
    id_target = re.compile(r'\d\d\d+')
    return id_target.findall(message.content)

def formatted_game_results(game_data):
    results = game_data['result']
    players = results.keys()
    scores = sorted(results.values(), reverse=True)
    formatted = []
    for score in scores:
        for player in players:
            if results[player] == score:
                formatted.append(f'{player} ({results[player]})')
    return '-- ' + ', '.join(formatted) + ' --'

async def auto_checker():
    while True:
        await check_all_games()
        await asyncio.sleep(10)

async def check_all_games():
    print('Checking all games.')

    conn = sqlite3.connect(games_db_fp)
    user_conn = sqlite3.connect(users_db_fp)

    games = sql_client.read_query(conn, 'SELECT * FROM games')
    for game in games:
        local_game_data = game
        game_id = local_game_data[0]
        channel = local_game_data[1]
        local_acting = local_game_data[2]
        web_game_data = fetch_game_data(game_id)
        target = client.get_channel(int(channel))

        if len(web_game_data['acting']) == 1:
            true_acting = str(web_game_data['acting'][0])
        else:
            true_acting = 'game over'
            
        if true_acting == 'game over':           
            game_results = formatted_game_results(web_game_data)     
            await target.send(f'Game over: {game_results}')
            sql_client.delete_game(conn, game_id)
            print(f'Deleted game {game_id} - game complete.')
        elif true_acting != local_acting:
            print(f'Updating game {game_id}.')
            acting_discord_id = sql_client.read_query(user_conn, 
                'SELECT discord_id FROM users WHERE web_id = ?', (true_acting,))
            mention = get_player_mention(true_acting)
            sql_client.update_acting_player(conn, game_id, true_acting)
            await target.send(verbage.discord_mention(mention, game_id))

    conn.close()
    user_conn.close()

### Bot Commands ###

async def bot_help(message):
    '''List of all accepted commands.'''

    await message.channel.send(verbage.help_message(help_command, track_command))

async def track_game(message):
    game_id_result = game_id_regex(message)
    channel_id = str(message.channel.id)

    conn = sql_client.connect(games_db_fp)
    userconn = sql_client.connect(users_db_fp)

    if len(game_id_result) != 1:
        await message.channel.send(verbage.game_id_error)
    else:
        game_id = game_id_result[0]
        game_data = fetch_game_data(game_id)

        if len(game_data['acting']) == 1:
            acting = str(game_data['acting'][0])
        else:
            acting = 'game over'

        already_in_db = sql_client.select_game(conn, game_id)
        if already_in_db:
            sql_client.update_game_channel(conn, channel_id, game_id)
        else:
            sql_client.insert_game(conn, game_id, channel_id, acting)

        web_players = game_data['players']
        local_players = sql_client.read_query(userconn, 'SELECT * FROM users')
        player_ids = [player[1] for player in local_players]
        player_names = [player[0] for player in local_players]

        for player in web_players:
            web_id = str(player['id'])
            web_name = player['name']
            if web_id not in player_ids:
                sql_client.insert_user(userconn, web_name, web_id, None)
            elif web_id in player_ids and web_name not in player_names:
                sql_client.execute_query(userconn, 
                'UPDATE users SET web_name = ? WHERE web_id = ?', (web_name, web_id))

        print(f'Tracking game ID {game_id} in channel ({channel_id}).')
        await message.channel.send(f'Tracking game ID {game_id} in this channel ({message.channel}).')

        conn.close()
        userconn.close()

async def sync_player_id(message):
    conn = sqlite3.connect(users_db_fp)

    new_name = message.content.split(' ', 1)[1]
    discord_id = str(message.author.id)
    local_players = sql_client.read_query(conn, 'SELECT * FROM users')
    player_names = [player[0] for player in local_players]

    if new_name in player_names:
        sql_client.execute_query(conn, 'UPDATE users SET discord_id = ? WHERE web_name = ?', (discord_id, new_name))
        await message.channel.send(f'Synced {message.author} as "{new_name}".')
        print(f'Synced {discord_id} as "{new_name}".')
    else:
        await message.channel.send(f'Username "{new_name}" not found, make sure you are in a tracked game first.')

    conn.close()

async def unsync_player_id(message):
    conn = sqlite3.connect(users_db_fp)

    target_name = message.content.split(' ', 1)[1]
    discord_id = str(message.author.id)
    local_players = sql_client.read_query(conn, 'SELECT * FROM users')
    player_names = [player[0] for player in local_players]

    if target_name in player_names:
        sql_client.execute_query(conn, 'UPDATE users SET discord_id = NULL WHERE web_name = ?', (target_name,))
        await message.channel.send(f'Unsynced {message.author} from "{target_name}".')
        print(f'Unsynced {discord_id} from "{target_name}".')
    else:
        await message.channel.send(f'Username "{target_name}" not found, make sure you are synced first.')

    conn.close()


### This Is "main", Sort Of ###

setup_users_db(users_db_fp)
setup_games_db(games_db_fp)

load_dotenv()
client.run(os.getenv('TOKEN'))