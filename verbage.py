def discord_mention(mention, game_id):
    return f'''{mention} - your turn! 
https://18xx.games/game/{game_id}'''

game_id_error = '''Sorry, I couldn't figure out the game ID :japanese_ogre:
Your command should look something like this: 
    !track https://18xx.games/game/25902
    or
    !track 25902'''

def help_message(help_command, track_command):
    return f'''
    Here are the commands I know:
        hello - I'll say hello back :)
        {help_command} - See this dialogue.
        {track_command} [game ID or link] - Track an async game for @mention notifications.
    All commands must be used in an open channel. When tracking a game, do so in the associated channel.
            '''