#!/usr/bin/env python3
#
# most of this is taken from the tutorial at:
# https://www.freecodecamp.org/news/create-a-discord-bot-with-python/

import discord, json, os

client = discord.Client()

busy = [] # Users who are in dialogue (ignore entry-level commands).

@client.event
async def on_ready():
    '''Status report!'''
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.author not in busy and str(message.channel.type) == 'private':
        if not message.content.startswith('!'):
            await message.channel.send('Hello! Say "!help" if you need help.')

        elif message.content.startswith('!help'):
            await botHelp(message)

        elif message.content.startswith('!newgame'):
            await newgame(message)


###


async def botHelp(message):
    '''List of all accepted commands.'''

    print(f'Responding to {message.author}: "!help"')
    await message.channel.send('''Here are the commands I know:
            hello - I'll say hello back :)
            !help - See this dialogue.
            !newgame - Schedule an upcoming game session.
            !schedule - List all currently scheduled games.''')


async def newgame(message):
    '''Enter a dialogue to schedule a game session.
    Mark user as "busy" until this is done or cancelled.'''
    #TODO break this huge function up
    
    channel = message.channel
    busy.append(message.author)
    newgame = {}

    def check(m):
        return m.channel == channel and m.author == message.author and m.author in busy

    async def cancel():
        busy.remove(message.author)
        await message.channel.send('Cancelling game creation.')
        await newgame.stop()

    await message.channel.send('Great, which game? Say !cancel to cancel.')
        
    game = await client.wait_for('message', check=check)
    if game.content == '!cancel':
        await cancel()
    newgame['title'] = game.content
    await channel.send(f'Scheduling {game.content}. On what date?')

    date = await client.wait_for('message', check=check)
    if date.content == '!cancel':
        await cancel()
    newgame['date'] = date.content

    schedule = {}

    with open('.log.json', 'r') as log:
        try:
            schedule = json.load(log)
        except json.decoder.JSONDecodeError:
            schedule = {"key" : 0}

    newkey = schedule['key'] + 1
    schedule['key'] = newkey
    schedule[newkey] = newgame

    with open('.log.json', 'w+') as log:
        json.dump(schedule, log)

    await channel.send(f'''Scheduled {game.content} on: {date.content}. \nI'll post it in #upcoming-games. Thanks!''')
    print(f'User {message.author} scheduled {game.content} for {date.content}.')

    busy.remove(message.author)


###


client.run(os.getenv('TOKEN'))