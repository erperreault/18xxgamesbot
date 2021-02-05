#!/usr/bin/env python3

import discord, json, os, urllib.request

client = discord.Client()
help_command = '!help'


###


def get_game_data(id: str) -> json:
    with urllib.request.urlopen(f'https://18xx.games/api/game/{id}') as response:
        return json.loads(response.read())

def get_all_player_ids(game: json) -> list:
    return [player['id'] for player in game['players']]

def get_acting_id(game: json) -> int:
    return game['acting'][0]

# for example    
my_game_id = '25902'
game_data = get_game_data(my_game_id)
print(get_acting_id(game_data))

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif str(message.channel.type) == 'private':
        if not message.content.startswith('!'):
            await message.channel.send(f'Hello! Say "{help_command}" if you need help.')

        elif message.content.startswith(help_command):
            await bot_help(message)

        else:
            await message.channel.send(f'Sorry, I don\'t know that command. Say "{help_command}" for the commands I do know.')


###


async def bot_help(message):
    '''List of all accepted commands.'''

    await message.channel.send(f'''Here are the commands I know:
            hello - I'll say hello back :)
            {help_command} - See this dialogue.''')


###


client.run(os.getenv('TOKEN'))