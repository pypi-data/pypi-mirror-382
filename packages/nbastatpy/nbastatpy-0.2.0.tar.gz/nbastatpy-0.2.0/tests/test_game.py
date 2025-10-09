from nbastatpy.game import Game

GAME_ID = "0021800836"


def test_game_creation():
    game = Game(GAME_ID)
    assert game.game_id == GAME_ID
