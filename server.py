#!/usr/bin/env python3
#
# most of this is taken from the tutorial at:
# https://www.freecodecamp.org/news/create-a-discord-bot-with-python/

import discord, json, os

client = discord.Client()
server = discord.Member().guild

help_command = '!help'

@client.event
async def on_ready():
    print(f'We have logged in as {client.user} on {server}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.author not in busy and str(message.channel.type) == 'private':
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