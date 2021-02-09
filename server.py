#!/usr/bin/env python3

import os, json, urllib.request, discord, re, asyncio, sql_client, sqlite3

### Constants ###

intents = discord.Intents.all()
client = discord.Client(intents = intents)
help_command = '!help'
track_command = '!track'
startup_command = '!startup'
sync_command = '!sync'
tracked_games_fp = '.tracked_games.json'
player_log_fp = '.player_log.json'

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
            
def get_game_data(id: str) -> str:
    with urllib.request.urlopen(f'https://18xx.games/api/game/{id}') as response:
        return json.loads(response.read())


def get_all_player_ids(game: str) -> list:
    return [player['id'] for player in game['players']]


def get_acting_id(game: str) -> str:
    try:
        return game['acting'][0]
    except:
        print('no acting player found')
        return 'none or game over'


def get_player_name_from_id(id, game):
    for player in game['players']:
        if player['id'] == int(id):
            return player['name']
    return id


def get_discord_mention_from_player_name(name, log):
    try:
        return f'<@{log[name]}>'
    except:
        return name


async def bot_help(message):
    '''List of all accepted commands.'''

    await message.channel.send(f'''Here are the commands I know:
            hello - I'll say hello back :)
            {help_command} - See this dialogue.
            {track_command} [game ID or link] - Track an async game for @mention notifications.''')


async def track_game(message):
    '''Associate a linked game ID with the channel it's given in.'''

    id_target = re.compile(r'\d\d\d+')
    id_results = id_target.findall(message.content)
    channel_id = str(message.channel.id)

    if len(id_results) != 1:
        await message.channel.send(
"""Sorry, I couldn't figure out the game ID :japanese_ogre:
Your command should look something like this: 
    !track https://18xx.games/game/25902
    or
    !track 25902""")
        
    else:
        game_id = id_results[0]
        game_data = get_game_data(game_id)
        players = game_data['players']
        print(players)
        for player in players:
            name = player['name']
            try:
                with open(player_log_fp, 'r') as player_log_file:
                    player_log = json.load(player_log_file)
            except:
                player_log = {}
            
            if name not in player_log.keys():
                player_log[name] = player['id']

        try:
            with open(tracked_games_fp, 'r') as log_file:
                game_log = json.load(log_file)
        except:
            game_log = {'channels': {}, 'games': {}}

        try:
            if game_id not in game_log['channels'][channel_id]:
                game_log['channels'][channel_id].append(game_id)
        except KeyError:
            game_log['channels'][channel_id] = [game_id]

        if game_id not in game_log['games'].keys():
            game_log['games'][game_id] = {}
        game_log['games'][game_id]['acting'] = get_acting_id(game_data)

        with open(tracked_games_fp, 'w') as log_file:
            json.dump(game_log, log_file)

        with open(player_log_fp, 'w') as player_log_file:
            json.dump(player_log, player_log_file)

        await message.channel.send(f'Tracking game ID {game_id} in this channel ({message.channel}).')
        print(f'Tracking {game_id} on channel {channel_id}.')


async def check_all_games():
    print('Checking all games.')
    try:
        with open(tracked_games_fp, 'r') as log_file:
            log = json.load(log_file)
    except:
        log = {'channels': {}, 'games': {}}
    try:
        with open(player_log_fp, 'r') as player_log_file:
            player_log = json.load(player_log_file)
    except:
        player_log = {}

    for channel in log['channels']:
        for game_id in log['channels'][channel]:
            game = get_game_data(game_id)
            true_acting = get_acting_id(game)
            acting_discord_name = get_player_name_from_id(true_acting, game)
            discord_mention = get_discord_mention_from_player_name(acting_discord_name, player_log)
            if log['games'][game_id]['acting'] != true_acting:
                print(f'Updating acting player for {game_id}: {true_acting}')
                log['games'][game_id]['acting'] = true_acting
                target = client.get_channel(int(channel))
                await target.send(f'''{discord_mention} - your turn! 
https://18xx.games/game/{game_id}''')

    with open(tracked_games_fp, 'w') as log_file:
        json.dump(log, log_file)


async def auto_checker():
    while True:
        await check_all_games()
        await asyncio.sleep(10)

async def sync_player_ids(message):
    web_name = message.content.split(' ', 1)[1]
    web_id = 'NULL'
    discord_id = str(message.author.id)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if sql_client.select_user(cursor, discord_id):
        sql_client.update_user(cursor, discord_id, web_name)
    else:
        sql_client.insert_user(cursor, web_name, web_id, discord_id)

    conn.commit()
    conn.close()

    await message.channel.send(f'Successfully synced {message.author} as {web_name}.')
    print(f'Synced {discord_id} as {web_name}.')

### This Is "main", Sort Of ###

client.run(os.getenv('TOKEN'))