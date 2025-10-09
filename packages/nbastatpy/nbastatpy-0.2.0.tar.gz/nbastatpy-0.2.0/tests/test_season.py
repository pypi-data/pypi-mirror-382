from nbastatpy.season import Season

SEASON_YEAR = "2020"


def test_season_creation():
    season = Season(SEASON_YEAR)
    assert season.season_year == int(SEASON_YEAR)
