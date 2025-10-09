from nbastatpy.team import Team

TEAM_NAME = "MIL"


def test_team_creation():
    team = Team(TEAM_NAME)
    assert team.info.get("abbreviation") == TEAM_NAME
