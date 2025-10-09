from nbastatpy.player import Player

PLAYER_NAME = "LeBron James"


def test_player_creation():
    player = Player(PLAYER_NAME)
    assert player.name == PLAYER_NAME
