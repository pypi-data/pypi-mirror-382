from datetime import datetime
from typing import Optional

import pandas as pd
from loguru import logger

from nbastatpy.config import (
    ColumnTypes,
    DateFields,
    IDFields,
    SpecialFields,
    TimeFields,
)


class DataStandardizer:
    """Base class for standardizing NBA data."""

    def __init__(self, df: pd.DataFrame, add_metadata: bool = False):
        """Initialize the DataStandardizer.

        Args:
            df: The DataFrame to standardize
            add_metadata: Whether to add metadata fields (standardized_at, etc.)
        """
        self.df = df.copy()
        self.add_metadata = add_metadata

    def standardize(self) -> pd.DataFrame:
        """Apply all standardization steps and return the standardized DataFrame.

        Returns:
            Standardized DataFrame
        """
        self.lowercase_columns()
        self.standardize_ids()
        self.standardize_dates()
        self.standardize_types()

        if self.add_metadata:
            self.add_metadata_fields()

        return self.df

    def lowercase_columns(self) -> None:
        """Convert all column names to lowercase."""
        self.df.columns = [col.lower() for col in self.df.columns]

    def standardize_ids(self) -> None:
        """Standardize ID columns: rename and zero-pad to 10 digits."""
        # First, rename inconsistent ID fields
        for old_name, new_name in IDFields.ID_FIELD_MAPPING.items():
            if old_name in self.df.columns:
                self.df = self.df.rename(columns={old_name: new_name})

        # Then, zero-pad all ID fields
        for id_field in IDFields.ID_FIELDS:
            if id_field in self.df.columns:
                try:
                    self.df[id_field] = (
                        self.df[id_field]
                        .astype(str)
                        .str.replace(".0", "", regex=False)
                        .str.zfill(10)
                    )
                except Exception as e:
                    logger.warning(f"Could not standardize ID field {id_field}: {e}")

    def standardize_dates(self) -> None:
        """Parse and standardize date columns."""
        for date_field in DateFields.DATE_FIELDS:
            if date_field in self.df.columns:
                try:
                    # Try pandas automatic parsing first
                    self.df[date_field] = pd.to_datetime(
                        self.df[date_field], errors="coerce"
                    ).dt.date
                except Exception as e:
                    logger.warning(f"Could not parse date field {date_field}: {e}")

    def standardize_types(self) -> None:
        """Convert columns to appropriate data types."""
        # Integer columns - try int first, fall back to float if needed
        for col in ColumnTypes.INTEGER_COLUMNS:
            if col in self.df.columns:
                # Convert to numeric, coercing errors to NaN
                numeric_col = pd.to_numeric(self.df[col], errors="coerce")

                # Check if all non-null values are integers
                if numeric_col.notna().any():
                    non_null = numeric_col.dropna()
                    if (non_null == non_null.astype(int)).all():
                        # All values are integers, use Int64
                        self.df[col] = numeric_col.astype("Int64")
                    else:
                        # Has decimal values, use float
                        self.df[col] = numeric_col

        # Float columns
        for col in ColumnTypes.FLOAT_COLUMNS:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        # String columns
        for col in ColumnTypes.STRING_COLUMNS:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str)

    def add_metadata_fields(self) -> None:
        """Add metadata fields like standardization timestamp."""
        self.df["standardized_at"] = datetime.now().isoformat()


class PlayerDataStandardizer(DataStandardizer):
    """Standardizer for player-specific data."""

    def standardize(self) -> pd.DataFrame:
        """Apply player-specific standardization steps.

        Returns:
            Standardized DataFrame
        """
        # Apply base standardization
        super().standardize()

        # Player-specific transformations
        self.convert_height()
        self.parse_birthdate()
        self.standardize_weight()
        self.standardize_position()

        return self.df

    def convert_height(self) -> None:
        """Convert height from feet-inches format (e.g., '6-11') to total inches."""
        for height_field in SpecialFields.HEIGHT_FIELDS:
            if height_field in self.df.columns:
                try:
                    # Split on hyphen and convert to inches
                    def parse_height(height_str):
                        if pd.isna(height_str) or height_str == "":
                            return None
                        parts = str(height_str).split("-")
                        if len(parts) == 2:
                            feet = int(parts[0])
                            inches = int(parts[1])
                            return feet * 12 + inches
                        return None

                    self.df["height_inches"] = self.df[height_field].apply(parse_height)
                except Exception as e:
                    logger.warning(
                        f"Could not convert height field {height_field}: {e}"
                    )

    def parse_birthdate(self) -> None:
        """Parse birthdate fields with special handling."""
        if "birthdate" in self.df.columns:
            try:
                self.df["birthdate"] = pd.to_datetime(
                    self.df["birthdate"], errors="coerce"
                ).dt.date
            except Exception as e:
                logger.warning(f"Could not parse birthdate: {e}")

    def standardize_weight(self) -> None:
        """Standardize weight to numeric pounds."""
        for weight_field in SpecialFields.WEIGHT_FIELDS:
            if weight_field in self.df.columns:
                try:
                    # Remove any text and convert to numeric
                    self.df[weight_field] = (
                        pd.to_numeric(
                            self.df[weight_field].astype(str).str.extract(r"(\d+)")[0],
                            errors="coerce",
                        )
                        .fillna(0)
                        .astype("Int64")
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not standardize weight field {weight_field}: {e}"
                    )

    def standardize_position(self) -> None:
        """Standardize position abbreviations."""
        position_fields = ["position", "pos", "player_position"]
        for pos_field in position_fields:
            if pos_field in self.df.columns:
                try:

                    def clean_position(pos):
                        if pd.isna(pos):
                            return None
                        pos_str = str(pos).upper().strip()
                        # Standardize common variations
                        position_map = {
                            "GUARD": "G",
                            "FORWARD": "F",
                            "CENTER": "C",
                            "POINT GUARD": "PG",
                            "SHOOTING GUARD": "SG",
                            "SMALL FORWARD": "SF",
                            "POWER FORWARD": "PF",
                            "G-F": "GF",
                            "F-G": "FG",
                            "F-C": "FC",
                            "C-F": "CF",
                        }
                        return position_map.get(pos_str, pos_str)

                    self.df[pos_field] = self.df[pos_field].apply(clean_position)
                except Exception as e:
                    logger.warning(
                        f"Could not standardize position field {pos_field}: {e}"
                    )


class GameDataStandardizer(DataStandardizer):
    """Standardizer for game-specific data."""

    def standardize(self) -> pd.DataFrame:
        """Apply game-specific standardization steps.

        Returns:
            Standardized DataFrame
        """
        # Apply base standardization
        super().standardize()

        # Game-specific transformations
        self.convert_minutes_to_seconds()
        self.convert_matchup_time()
        self.convert_clock_time()
        self.parse_matchup_string()
        self.standardize_wl()

        return self.df

    def convert_minutes_to_seconds(self) -> None:
        """Convert MM:SS format to total seconds for minutes fields."""
        for field in TimeFields.MINUTES_SECONDS_FIELDS:
            if field in self.df.columns:
                try:

                    def parse_time(time_str):
                        if pd.isna(time_str) or time_str == "":
                            return None
                        parts = str(time_str).split(":")
                        if len(parts) == 2:
                            minutes = int(parts[0])
                            seconds = int(float(parts[1]))
                            return minutes * 60 + seconds
                        return None

                    seconds_field = field.replace("minutes", "seconds").replace(
                        "min", "seconds"
                    )
                    self.df[seconds_field] = self.df[field].apply(parse_time)
                except Exception as e:
                    logger.warning(f"Could not convert time field {field}: {e}")

    def convert_matchup_time(self) -> None:
        """Convert matchupminutes to matchup_seconds."""
        if "matchupminutes" in self.df.columns:
            try:

                def parse_matchup_time(time_str):
                    if pd.isna(time_str) or time_str == "":
                        return None
                    parts = str(time_str).split(":")
                    if len(parts) == 2:
                        minutes = int(parts[0])
                        seconds = int(float(parts[1]))
                        return minutes * 60 + seconds
                    return None

                self.df["matchup_seconds"] = self.df["matchupminutes"].apply(
                    parse_matchup_time
                )
            except Exception as e:
                logger.warning(f"Could not convert matchupminutes: {e}")

    def convert_clock_time(self) -> None:
        """Process play-by-play clock format (e.g., 'PT11M23.45S')."""
        if "clock" in self.df.columns:
            try:

                def parse_clock(clock_str):
                    if pd.isna(clock_str) or clock_str == "":
                        return None
                    import re

                    # Extract minutes and seconds from format like PT11M23.45S
                    minutes_match = re.search(r"(\d+)M", str(clock_str))
                    seconds_match = re.search(r"M(\d+(?:\.\d+)?)S", str(clock_str))

                    if minutes_match and seconds_match:
                        minutes = int(minutes_match.group(1))
                        seconds = float(seconds_match.group(1))
                        return minutes * 60 + seconds
                    return None

                self.df["clock_seconds"] = self.df["clock"].apply(parse_clock)
            except Exception as e:
                logger.warning(f"Could not convert clock time: {e}")

    def parse_matchup_string(self) -> None:
        """Parse matchup strings like 'TOR @ BOS' into home/away teams."""
        for matchup_field in SpecialFields.MATCHUP_FIELDS:
            if matchup_field in self.df.columns:
                try:

                    def extract_teams(matchup_str):
                        if pd.isna(matchup_str) or matchup_str == "":
                            return None, None
                        parts = str(matchup_str).split()
                        if len(parts) >= 3:
                            if "@" in parts:
                                idx = parts.index("@")
                                away_team = parts[idx - 1] if idx > 0 else None
                                home_team = (
                                    parts[idx + 1] if idx < len(parts) - 1 else None
                                )
                                return away_team, home_team
                            elif "vs." in parts or "vs" in parts:
                                vs_idx = (
                                    parts.index("vs.")
                                    if "vs." in parts
                                    else parts.index("vs")
                                )
                                home_team = parts[vs_idx - 1] if vs_idx > 0 else None
                                away_team = (
                                    parts[vs_idx + 1]
                                    if vs_idx < len(parts) - 1
                                    else None
                                )
                                return away_team, home_team
                        return None, None

                    # Extract home and away teams
                    teams = self.df[matchup_field].apply(extract_teams)
                    self.df["away_team"] = teams.apply(lambda x: x[0] if x else None)
                    self.df["home_team"] = teams.apply(lambda x: x[1] if x else None)
                except Exception as e:
                    logger.warning(
                        f"Could not parse matchup field {matchup_field}: {e}"
                    )

    def standardize_wl(self) -> None:
        """Standardize win/loss indicator fields to consistent format."""
        for wl_field in SpecialFields.WL_FIELDS:
            if wl_field in self.df.columns:
                try:

                    def standardize_outcome(val):
                        if pd.isna(val):
                            return None
                        val_str = str(val).upper().strip()
                        if val_str in ["W", "WIN", "WON", "1", "TRUE"]:
                            return "W"
                        elif val_str in ["L", "LOSS", "LOST", "0", "FALSE"]:
                            return "L"
                        return val_str

                    self.df[wl_field] = self.df[wl_field].apply(standardize_outcome)
                except Exception as e:
                    logger.warning(f"Could not standardize W/L field {wl_field}: {e}")


class SeasonDataStandardizer(DataStandardizer):
    """Standardizer for season-specific data."""

    def __init__(
        self,
        df: pd.DataFrame,
        season: Optional[str] = None,
        playoffs: bool = False,
        add_metadata: bool = False,
    ):
        """Initialize the SeasonDataStandardizer.

        Args:
            df: The DataFrame to standardize
            season: Season ID (e.g., '2023-24')
            playoffs: Whether this is playoff data
            add_metadata: Whether to add metadata fields
        """
        super().__init__(df, add_metadata)
        self.season = season
        self.playoffs = playoffs

    def standardize(self) -> pd.DataFrame:
        """Apply season-specific standardization steps.

        Returns:
            Standardized DataFrame
        """
        # Apply base standardization
        super().standardize()

        # Season-specific transformations
        self.add_season_id()
        self.add_playoff_flag()
        self.parse_game_dates()

        return self.df

    def add_season_id(self) -> None:
        """Add season_id column if season is provided."""
        if self.season and "season_id" not in self.df.columns:
            self.df["season_id"] = self.season

    def add_playoff_flag(self) -> None:
        """Add or standardize playoff indicator."""
        if "is_playoffs" not in self.df.columns:
            self.df["is_playoffs"] = "PLAYOFFS" if self.playoffs else "REGULAR_SEASON"
        else:
            # Standardize existing playoff flags
            def standardize_playoff_flag(val):
                if pd.isna(val):
                    return "REGULAR_SEASON"
                val_str = str(val).upper()
                if "PLAYOFF" in val_str or val_str == "TRUE" or val_str == "1":
                    return "PLAYOFFS"
                return "REGULAR_SEASON"

            self.df["is_playoffs"] = self.df["is_playoffs"].apply(
                standardize_playoff_flag
            )

    def parse_game_dates(self) -> None:
        """Parse game_date fields with various formats."""
        if "game_date" in self.df.columns:
            try:
                self.df["game_date"] = pd.to_datetime(
                    self.df["game_date"], errors="coerce"
                ).dt.date
            except Exception as e:
                logger.warning(f"Could not parse game_date: {e}")


class TeamDataStandardizer(DataStandardizer):
    """Standardizer for team-specific data."""

    def __init__(
        self,
        df: pd.DataFrame,
        season: Optional[str] = None,
        playoffs: bool = False,
        add_metadata: bool = False,
    ):
        """Initialize the TeamDataStandardizer.

        Args:
            df: The DataFrame to standardize
            season: Season ID (e.g., '2023-24')
            playoffs: Whether this is playoff data
            add_metadata: Whether to add metadata fields
        """
        super().__init__(df, add_metadata)
        self.season = season
        self.playoffs = playoffs

    def standardize(self) -> pd.DataFrame:
        """Apply team-specific standardization steps.

        Returns:
            Standardized DataFrame
        """
        # Apply base standardization
        super().standardize()

        # Team-specific transformations
        self.add_season_metadata()

        return self.df

    def add_season_metadata(self) -> None:
        """Add season and playoff metadata if not present."""
        if self.season and "season" not in self.df.columns:
            self.df["season"] = self.season

        if "season_type" not in self.df.columns:
            self.df["season_type"] = "Playoffs" if self.playoffs else "Regular Season"


def standardize_dataframe(
    df: pd.DataFrame,
    data_type: str = "base",
    season: Optional[str] = None,
    playoffs: bool = False,
    add_metadata: bool = False,
) -> pd.DataFrame:
    """Standardize a DataFrame based on its type.

    Args:
        df: The DataFrame to standardize
        data_type: Type of data ('player', 'game', 'season', 'team', or 'base')
        season: Season ID for season/team data
        playoffs: Whether this is playoff data
        add_metadata: Whether to add metadata fields

    Returns:
        Standardized DataFrame

    Example:
        >>> df = player.get_common_info()
        >>> standardized_df = standardize_dataframe(df, data_type='player')
    """
    standardizers = {
        "player": PlayerDataStandardizer,
        "game": GameDataStandardizer,
        "season": SeasonDataStandardizer,
        "team": TeamDataStandardizer,
        "base": DataStandardizer,
    }

    standardizer_class = standardizers.get(data_type.lower(), DataStandardizer)

    # Create standardizer with appropriate arguments
    if data_type.lower() in ["season", "team"]:
        standardizer = standardizer_class(
            df, season=season, playoffs=playoffs, add_metadata=add_metadata
        )
    else:
        standardizer = standardizer_class(df, add_metadata=add_metadata)

    return standardizer.standardize()
