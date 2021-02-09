#!/usr/bin/env python3

import os, json, urllib.request, discord, re, asyncio, sql_client, sqlite3

### Constants ###
client = discord.Client()
help_command = '!help'
track_command = '!track'
startup_command = '!startup'
sync_command = '!sync'
tracked_games_fp = '.tracked_games.json'
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

        if message.content.startswith(sync_command):
            await sync_player_ids(message)

    elif str(message.channel.type) == 'private' and message.author != client.user:

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
    cursor = conn.cursor()

    sql_client.make_user_table(cursor)

    conn.commit()
    conn.close()
    
def setup_games_db(game_db_fp):
    conn = sqlite3.connect(games_db_fp)
    cursor = conn.cursor()

    sql_client.make_games_table(cursor)

    conn.commit()
    conn.close()
            
def fetch_game_data(id: str) -> str:
    with urllib.request.urlopen(f'https://18xx.games/api/game/{id}') as response:
        return json.loads(response.read())


def get_discord_mention_from_web_id(web_id, log):
    pass


async def bot_help(message):
    '''List of all accepted commands.'''

    await message.channel.send(f'''Here are the commands I know:
            hello - I'll say hello back :)
            {help_command} - See this dialogue.
            {track_command} [game ID or link] - Track an async game for @mention notifications.''')


async def track_game(message):
    id_target = re.compile(r'\d\d\d+')
    id_results = id_target.findall(message.content)
    channel_id = str(message.channel.id)

    if len(id_results) != 1:
        await message.channel.send(
'''Sorry, I couldn't figure out the game ID :japanese_ogre:
Your command should look something like this: 
    !track https://18xx.games/game/25902
    or
    !track 25902''')

    else:
        game_id = id_results[0]
        game_data = fetch_game_data(game_id)
        players = game_data['players']

        conn = sqlite3.connect(games_db_fp)
        gcursor = conn.cursor()

        if len(game_data['acting']) == 1:
            acting = str(game_data['acting'][0])
        else:
            acting = 'game over'

        if game_id not in gcursor.execute('SELECT game_id FROM games').fetchall():
            sql_client.insert_game(gcursor, game_id, channel_id, acting)
        else:
            gcursor.execute('UPDATE games SET channel = ? WHERE game_id = ?', (channel_id, game_id))

        await message.channel.send(f'Now tracking game ID {game_id} in this channel ({message.channel}).')

        conn.commit()
        conn.close()


async def check_all_games():
    print('Checking all games.')

    conn = sqlite3.connect(games_db_fp)
    cursor = conn.cursor()

    game_ids = cursor.execute('SELECT game_id FROM games').fetchall()
    for game_id in game_ids:
        local_game_data = cursor.execute('SELECT * FROM games WHERE game_id = ?', game_id).fetchone()
        game_id = local_game_data[0]
        channel = local_game_data[1]
        local_acting = local_game_data[2]
        web_game_data = fetch_game_data(game_id)

        if len(web_game_data['acting']) == 1:
            true_acting = str(web_game_data['acting'][0])
        else:
            true_acting = 'game over'

        target = client.get_channel(int(channel))
        if true_acting == 'game over':                
            await target.send(f'Game over! More on this later.')
            #TODO finish this ^
        elif true_acting != local_acting:
            sql_client.update_acting_player(cursor, game_id, true_acting)
            await target.send(f'''{true_acting} - your turn! 
https://18xx.games/game/{game_id}''')

    conn.commit()
    conn.close()


async def auto_checker():
    while True:
        await check_all_games()
        await asyncio.sleep(10)


async def sync_player_ids(message):
    web_name = message.content.split(' ', 1)[1]
    web_id = 'NULL'
    discord_id = str(message.author.id)

    conn = sqlite3.connect(player_log_fp)
    cursor = conn.cursor()

    if sql_client.select_user(cursor, discord_id):
        sql_client.update_user(cursor, discord_id, web_name)
    else:
        sql_client.insert_user(cursor, web_name, web_id, discord_id)

    conn.commit()
    conn.close()

    await message.channel.send(f'Synced {message.author} as {web_name}.')
    print(f'Synced {discord_id} as {web_name}.')


### This Is "main", Sort Of ###


setup_users_db(users_db_fp)
setup_games_db(games_db_fp)

client.run(os.getenv('TOKEN'))