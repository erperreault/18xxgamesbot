#!/usr/bin/env python3
#
# most of this is taken from the tutorial at:
# https://www.freecodecamp.org/news/create-a-discord-bot-with-python/

import discord, json, os

client = discord.Client()
busy = []

@client.event
async def on_ready():
    '''Status report!'''
    print(f'We have logged in as {client.user}')

# Herein lie message events.
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.author not in busy and str(message.channel.type) == 'private':
        if not message.content.startswith('!'):
            await message.channel.send('Hello! Say "!help" if you need help.')

        elif message.content.startswith('!help'):
            await bot_help(message)

        elif message.content.startswith('!newgame'):
            await newgame(message)


###


async def bot_help(message):
    '''List of all accepted commands.'''

    await message.channel.send('''Here are the commands I know:
            hello - I'll say hello back :)
            !help - See this dialogue.
            !newgame - Schedule an upcoming game session.
            !schedule - List all currently scheduled games.''')

async def newgame(message):
    '''Enter a dialogue to schedule a game session.
    Mark user as "busy" until this is done or cancelled.'''
    
    global busy
    channel = message.channel
    author = message.author
    newgame_dict = {}

    def identity_check(message):
        return message.channel == channel and message.author == author and message.author in busy

    async def cancel(message):
        busy.remove(author)
        await message.channel.send('Cancelling game creation.')
        await newgame.cancel()

    async def savegame(entry):
        '''Imports .log.json. 
        Start file in format if empty. 
        Add new game to the lineup with a unique ID.'''
        with open('.log.json', 'r') as log:
            try:
                schedule = json.load(log)
            except json.decoder.JSONDecodeError:
                schedule = {"key" : 0}

        newkey = schedule['key'] + 1
        schedule['key'] = newkey
        schedule[newkey] = entry

        with open('.log.json', 'w+') as log:
            json.dump(schedule, log)

    async def check_for_cancel():
        '''First check that message is in the same thread, then check for '!cancel'.'''
        x = await client.wait_for('message', check=identity_check)
        if x.content == '!cancel':
            await cancel(message)
        return x.content

    busy.append(author)

    await channel.send('Great, which game? Say !cancel to cancel.')
        
    title = await check_for_cancel()
    newgame_dict['title'] = title
    await channel.send(f'Scheduling {title}. On what date? Please format like so: 24jan, or 15mar.')

    date = await check_for_cancel()
    newgame_dict['date'] = date

    await savegame(newgame_dict)

    await channel.send(f"Scheduled {title} on {date}. I'll make a channel for it. Thanks!")
    print(f'User {author} scheduled {title} for {date}.') 

    busy.remove(author)


###


client.run(os.getenv('TOKEN'))