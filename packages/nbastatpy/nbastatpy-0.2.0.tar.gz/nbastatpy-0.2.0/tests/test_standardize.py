import pandas as pd

from nbastatpy.standardize import (
    DataStandardizer,
    GameDataStandardizer,
    PlayerDataStandardizer,
    SeasonDataStandardizer,
    TeamDataStandardizer,
    standardize_dataframe,
)


class TestDataStandardizer:
    """Test the base DataStandardizer class."""

    def test_lowercase_columns(self):
        """Test that column names are converted to lowercase."""
        df = pd.DataFrame({"PLAYER_ID": [1], "TEAM_ID": [2], "GAME_ID": [3]})
        standardizer = DataStandardizer(df)
        standardizer.lowercase_columns()
        assert list(standardizer.df.columns) == ["player_id", "team_id", "game_id"]

    def test_standardize_ids(self):
        """Test that IDs are zero-padded to 10 digits."""
        df = pd.DataFrame({"player_id": [123, 456], "team_id": [1, 2]})
        standardizer = DataStandardizer(df)
        standardizer.standardize_ids()
        assert standardizer.df["player_id"].iloc[0] == "0000000123"
        assert standardizer.df["team_id"].iloc[0] == "0000000001"

    def test_standardize_ids_with_float(self):
        """Test that IDs with .0 are handled correctly."""
        df = pd.DataFrame({"player_id": [123.0, 456.0]})
        standardizer = DataStandardizer(df)
        standardizer.standardize_ids()
        assert standardizer.df["player_id"].iloc[0] == "0000000123"

    def test_standardize_dates(self):
        """Test that date fields are parsed correctly."""
        df = pd.DataFrame({"game_date": ["2024-01-15", "2024-02-20"]})
        standardizer = DataStandardizer(df)
        standardizer.standardize_dates()
        assert pd.api.types.is_object_dtype(
            standardizer.df["game_date"]
        ) or pd.api.types.is_datetime64_any_dtype(standardizer.df["game_date"])

    def test_add_metadata_fields(self):
        """Test that metadata fields are added."""
        df = pd.DataFrame({"player_id": [123]})
        standardizer = DataStandardizer(df, add_metadata=True)
        standardizer.add_metadata_fields()
        assert "standardized_at" in standardizer.df.columns

    def test_full_standardization(self):
        """Test full standardization process."""
        df = pd.DataFrame(
            {
                "PLAYER_ID": [123],
                "TEAM_ID": [1],
                "PTS": [25],
                "FG_PCT": [0.5],
                "PLAYER_NAME": ["Test Player"],
            }
        )
        standardizer = DataStandardizer(df)
        result = standardizer.standardize()

        # Check columns are lowercase
        assert all(col.islower() for col in result.columns)

        # Check IDs are padded
        assert result["player_id"].iloc[0] == "0000000123"


class TestPlayerDataStandardizer:
    """Test the PlayerDataStandardizer class."""

    def test_convert_height(self):
        """Test height conversion from feet-inches to total inches."""
        df = pd.DataFrame({"height": ["6-11", "7-2"]})
        standardizer = PlayerDataStandardizer(df)
        standardizer.convert_height()
        assert "height_inches" in standardizer.df.columns
        assert standardizer.df["height_inches"].iloc[0] == 83  # 6*12 + 11
        assert standardizer.df["height_inches"].iloc[1] == 86  # 7*12 + 2

    def test_parse_birthdate(self):
        """Test birthdate parsing."""
        df = pd.DataFrame({"birthdate": ["1990-01-15T00:00:00", "1985-05-20T00:00:00"]})
        standardizer = PlayerDataStandardizer(df)
        standardizer.parse_birthdate()
        assert pd.api.types.is_object_dtype(
            standardizer.df["birthdate"]
        ) or pd.api.types.is_datetime64_any_dtype(standardizer.df["birthdate"])


class TestGameDataStandardizer:
    """Test the GameDataStandardizer class."""

    def test_convert_minutes_to_seconds(self):
        """Test conversion of MM:SS to seconds."""
        df = pd.DataFrame({"min": ["12:30", "5:45"]})
        standardizer = GameDataStandardizer(df)
        standardizer.convert_minutes_to_seconds()
        assert "seconds" in standardizer.df.columns
        assert standardizer.df["seconds"].iloc[0] == 750  # 12*60 + 30
        assert standardizer.df["seconds"].iloc[1] == 345  # 5*60 + 45

    def test_convert_matchup_time(self):
        """Test conversion of matchupminutes to seconds."""
        df = pd.DataFrame({"matchupminutes": ["10:15", "3:20"]})
        standardizer = GameDataStandardizer(df)
        standardizer.convert_matchup_time()
        assert "matchup_seconds" in standardizer.df.columns
        assert standardizer.df["matchup_seconds"].iloc[0] == 615  # 10*60 + 15

    def test_convert_clock_time(self):
        """Test conversion of play-by-play clock format."""
        df = pd.DataFrame({"clock": ["PT11M23S", "PT5M45.5S"]})
        standardizer = GameDataStandardizer(df)
        standardizer.convert_clock_time()
        assert "clock_seconds" in standardizer.df.columns
        assert standardizer.df["clock_seconds"].iloc[0] == 683  # 11*60 + 23


class TestSeasonDataStandardizer:
    """Test the SeasonDataStandardizer class."""

    def test_add_season_id(self):
        """Test that season_id is added."""
        df = pd.DataFrame({"player_id": [123]})
        standardizer = SeasonDataStandardizer(df, season="2023-24")
        standardizer.add_season_id()
        assert "season_id" in standardizer.df.columns
        assert standardizer.df["season_id"].iloc[0] == "2023-24"

    def test_add_playoff_flag(self):
        """Test that playoff flag is added."""
        df = pd.DataFrame({"player_id": [123]})
        standardizer = SeasonDataStandardizer(df, playoffs=True)
        standardizer.add_playoff_flag()
        assert "is_playoffs" in standardizer.df.columns
        assert standardizer.df["is_playoffs"].iloc[0] == "PLAYOFFS"

    def test_parse_game_dates(self):
        """Test game date parsing."""
        df = pd.DataFrame({"game_date": ["2024-01-15", "2024-02-20"]})
        standardizer = SeasonDataStandardizer(df)
        standardizer.parse_game_dates()
        assert pd.api.types.is_object_dtype(
            standardizer.df["game_date"]
        ) or pd.api.types.is_datetime64_any_dtype(standardizer.df["game_date"])


class TestTeamDataStandardizer:
    """Test the TeamDataStandardizer class."""

    def test_add_season_metadata(self):
        """Test that season metadata is added."""
        df = pd.DataFrame({"team_id": [1]})
        standardizer = TeamDataStandardizer(df, season="2023-24", playoffs=False)
        standardizer.add_season_metadata()
        assert "season" in standardizer.df.columns
        assert "season_type" in standardizer.df.columns
        assert standardizer.df["season"].iloc[0] == "2023-24"
        assert standardizer.df["season_type"].iloc[0] == "Regular Season"


class TestStandardizeDataframe:
    """Test the standardize_dataframe helper function."""

    def test_standardize_player_data(self):
        """Test standardizing player data."""
        df = pd.DataFrame(
            {
                "PLAYER_ID": [123],
                "HEIGHT": ["6-11"],
                "PTS": [25],
            }
        )
        result = standardize_dataframe(df, data_type="player")
        assert "player_id" in result.columns
        assert result["player_id"].iloc[0] == "0000000123"
        assert "height_inches" in result.columns

    def test_standardize_game_data(self):
        """Test standardizing game data."""
        df = pd.DataFrame(
            {
                "GAME_ID": [12345],
                "MIN": ["12:30"],
            }
        )
        result = standardize_dataframe(df, data_type="game")
        assert "game_id" in result.columns
        assert "seconds" in result.columns

    def test_standardize_season_data(self):
        """Test standardizing season data."""
        df = pd.DataFrame(
            {
                "PLAYER_ID": [123],
                "PTS": [25],
            }
        )
        result = standardize_dataframe(
            df, data_type="season", season="2023-24", playoffs=True
        )
        assert "season_id" in result.columns
        assert "is_playoffs" in result.columns
        assert result["is_playoffs"].iloc[0] == "PLAYOFFS"

    def test_standardize_team_data(self):
        """Test standardizing team data."""
        df = pd.DataFrame(
            {
                "TEAM_ID": [1],
                "PTS": [110],
            }
        )
        result = standardize_dataframe(
            df, data_type="team", season="2023-24", playoffs=False
        )
        assert "season" in result.columns
        assert result["season"].iloc[0] == "2023-24"

    def test_standardize_base_data(self):
        """Test standardizing with base standardizer."""
        df = pd.DataFrame(
            {
                "PLAYER_ID": [123],
                "TEAM_ID": [1],
            }
        )
        result = standardize_dataframe(df, data_type="base")
        assert all(col.islower() for col in result.columns)
        assert result["player_id"].iloc[0] == "0000000123"
