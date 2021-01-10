#!/usr/bin/env python
#
# most of this is taken from the tutorial at:
# https://www.freecodecamp.org/news/create-a-discord-bot-with-python/

import discord
import os

client = discord.Client()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello, currently this is all I know.')

client.run(os.getenv('TOKEN'))