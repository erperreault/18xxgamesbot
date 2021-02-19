import unittest, re, sql_client
from unittest.mock import MagicMock
from server import game_id_regex
from server import formatted_game_results
from server import get_player_mention

class TestGameIdRegex(unittest.TestCase):

    def test_id_in_url(self):
        self.assertEqual(game_id_regex('https://18xx.games/game/90210'), '90210')

    def test_id_alone(self):
        self.assertEqual(game_id_regex('90210'), '90210')

    def test_id_multiple(self):
        self.assertEqual(game_id_regex('90210 90210 90210'), '')

    def test_no_id(self):
        self.assertEqual(game_id_regex('blah blah blah'), '')

    def test_none(self):
        self.assertEqual(game_id_regex(None), '')

class TestFormattedGameResults(unittest.TestCase):

    def test_id_in_url(self):
        return
        self.assertEqual(formatted_game_results('https://18xx.games/game/90210'), '90210')

class TestGetPlayerMention(unittest.TestCase):

    sql_client.select_user_by_web_id = MagicMock(return_value=[['webname', 'webid', 'discordid']])

    def test_id_in_url(self):
        self.assertEqual(get_player_mention('webid', ''), '<@discordid>')

def get_player_mention(web_id, conn):
    player = sql_client.select_user_by_web_id(conn, web_id)[0]
    web_name = player[0]
    discord_id = player[2]
    if not discord_id:
        return web_name 
    else:
        return f'<@{discord_id}>'






































if __name__ == '__main__':
    unittest.main()