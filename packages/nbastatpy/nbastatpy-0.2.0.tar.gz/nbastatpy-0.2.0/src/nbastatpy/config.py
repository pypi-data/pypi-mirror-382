from typing import Dict, List, Set


class ColumnTypes:
    """Standard column type mappings for common NBA data fields."""

    # Numeric types - Integer columns
    INTEGER_COLUMNS: Set[str] = {
        # Basic info
        "age",
        "season_year",
        "draft_year",
        "draft_round",
        "draft_number",
        # Games and results
        "games",
        "games_played",
        "gp",
        "gs",
        "games_started",
        "w",
        "l",
        "wins",
        "losses",
        "win_streak",
        "lose_streak",
        # Traditional stats - field goals
        "fgm",
        "fga",
        "fg3m",
        "fg3a",
        "fg2m",
        "fg2a",
        "ftm",
        "fta",
        # Traditional stats - rebounds
        "oreb",
        "dreb",
        "reb",
        "oreb_pct_rank",
        "dreb_pct_rank",
        # Traditional stats - other
        "ast",
        "stl",
        "blk",
        "tov",
        "pf",
        "pts",
        "plus_minus",
        "pm",
        # Ranking columns
        "rank",
        "w_rank",
        "l_rank",
        "w_pct_rank",
        # Advanced stat counts
        "contested_shots",
        "deflections",
        "loose_balls_recovered",
        "charges_drawn",
        "screen_assists",
        "box_outs",
        # Tracking counts
        "touches",
        "front_ct_touches",
        "elbow_touches",
        "post_touches",
        "paint_touches",
        "passes",
        "ast_pass",
        "secondary_ast",
        "potential_ast",
        "drives",
        # Synergy/play type counts
        "poss",
        "possessions",
        # Shot location counts
        "restricted_area_fgm",
        "restricted_area_fga",
        "paint_fgm",
        "paint_fga",
        "midrange_fgm",
        "midrange_fga",
        "left_corner_three_fgm",
        "left_corner_three_fga",
        "right_corner_three_fgm",
        "right_corner_three_fga",
        "above_break_three_fgm",
        "above_break_three_fga",
        "corner_three_fgm",
        "corner_three_fga",
        "backcourt_fgm",
        "backcourt_fga",
        # Play-by-play
        "period",
        "quarter",
        "score_margin",
    }

    # Float columns - Percentages, rates, and continuous metrics
    FLOAT_COLUMNS: Set[str] = {
        # Shooting percentages
        "fg_pct",
        "fg2_pct",
        "fg3_pct",
        "ft_pct",
        "ts_pct",
        "efg_pct",
        # Advanced percentages
        "ast_pct",
        "ast_to",
        "ast_ratio",
        "reb_pct",
        "oreb_pct",
        "dreb_pct",
        "usg_pct",
        "tov_pct",
        "stl_pct",
        "blk_pct",
        "tm_tov_pct",
        # Win/pace metrics
        "w_pct",
        "pace",
        "pie",
        "net_rating",
        "off_rating",
        "def_rating",
        "ortg",
        "drtg",
        # Time metrics
        "min",
        "minutes",
        "min_pct",
        "time_of_poss",
        "avg_sec_per_touch",
        "avg_drib_per_touch",
        # Physical measurements
        "height_inches",
        "weight",
        # Distance metrics
        "dist_feet",
        "dist_miles",
        "avg_speed",
        "avg_speed_off",
        "avg_speed_def",
        # Shot location percentages
        "restricted_area_fg_pct",
        "paint_fg_pct",
        "midrange_fg_pct",
        "left_corner_three_fg_pct",
        "right_corner_three_fg_pct",
        "above_break_three_fg_pct",
        "corner_three_fg_pct",
        "backcourt_fg_pct",
        # Shot type percentages
        "catch_shoot_fg_pct",
        "pull_up_fg_pct",
        "less_than_6_fg_pct",
        "less_than_10_fg_pct",
        "greater_than_15_fg_pct",
        # Four factors
        "efg_pct_rank",
        "fta_rate",
        "tm_tov_pct_rank",
        "oreb_pct_rank_val",
        # Synergy metrics
        "percentile",
        "ppp",
        "points_per_possession",
        "freq",
        "frequency",
        # Passing metrics
        "ast_pts_created",
        "ast_adj",
        "passes_made",
        "passes_received",
        # Matchup metrics
        "partial_poss",
        "player_pts",
        "matchup_ast",
        "matchup_tov",
        "matchup_blk",
        "matchup_fgm",
        "matchup_fga",
        "matchup_fg_pct",
        "help_blk",
        "help_blk_pct",
        # Defense metrics
        "dfg_pct",
        "diff_pct",
        "normal_fg_pct",
        # Salary
        "salary",
        "adj_salary",
    }

    # String types
    STRING_COLUMNS: Set[str] = {
        # Player info
        "player_name",
        "player_first_name",
        "player_last_name",
        "first_name",
        "last_name",
        "display_first_last",
        "display_last_comma_first",
        "display_fi_last",
        "player_slug",
        # Team info
        "team_name",
        "team_abbreviation",
        "team_slug",
        "team_city",
        "team_nickname",
        "abbrev",
        # Position
        "position",
        "pos",
        "player_position",
        # Geographic info
        "college",
        "country",
        "birthplace",
        "school",
        # Game info
        "matchup",
        "wl",
        "video_available",
        # Lineup info
        "group_name",
        "group_id",
        # Matchup strings
        "off_player_name",
        "def_player_name",
        # Play type
        "play_type",
        "type_grouping",
        # General categorical
        "season_type",
        "season_type_all_star",
        "is_playoffs",
        "outcome",
        "location",
        # Additional identifiers
        "nickname",
        "rosterstatus",
        "how_acquired",
    }


class IDFields:
    """Registry of ID fields and their standardization rules."""

    # Fields that should be zero-padded to 10 digits
    ID_FIELDS: Set[str] = {
        "player_id",
        "team_id",
        "game_id",
        "person_id",
        "playerid",
        "teamid",
        "gameid",
        "personid",
        "off_player_id",
        "def_player_id",
        "vs_player_id",
        "player1_id",
        "player2_id",
        "player3_id",
        "player4_id",
        "player5_id",
    }

    # Mapping of inconsistent ID field names to standardized names
    ID_FIELD_MAPPING: Dict[str, str] = {
        "gameid": "game_id",
        "teamid": "team_id",
        "playerid": "player_id",
        "person_id": "player_id",
        "personid": "player_id",
    }


class DateFields:
    """Registry of date fields and parsing formats."""

    # Fields that should be parsed as dates
    DATE_FIELDS: Set[str] = {
        "game_date",
        "birthdate",
        "birth_date",
        "from_year",
        "to_year",
    }

    # Date parsing formats to try (in order)
    DATE_FORMATS: List[str] = [
        "%Y-%m-%dT%H:%M:%S",  # ISO with time
        "%Y-%m-%d",  # ISO date
        "%m/%d/%Y",  # US format
        "%d/%m/%Y",  # International format
    ]


class TimeFields:
    """Registry of time fields that need conversion."""

    # Fields in MM:SS format that should be converted to seconds
    MINUTES_SECONDS_FIELDS: Set[str] = {
        "min",
        "minutes",
        "matchupminutes",
    }

    # Fields that represent seconds already
    SECONDS_FIELDS: Set[str] = {
        "seconds",
        "matchup_seconds",
        "clock_seconds",
    }


class SpecialFields:
    """Special field handling rules."""

    # Fields that indicate playoff vs regular season
    PLAYOFF_INDICATORS: Set[str] = {
        "season_type",
        "season_type_all_star",
        "is_playoffs",
    }

    # Height fields (in feet-inches format like "6-11")
    HEIGHT_FIELDS: Set[str] = {
        "height",
        "player_height",
    }

    # Weight fields (in pounds)
    WEIGHT_FIELDS: Set[str] = {
        "weight",
        "player_weight",
    }

    # Matchup fields that need parsing (e.g., "TOR @ BOS")
    MATCHUP_FIELDS: Set[str] = {
        "matchup",
        "game_matchup",
    }

    # Win/Loss indicator fields
    WL_FIELDS: Set[str] = {
        "wl",
        "w_l",
        "outcome",
    }

    # Lineup/group name fields that contain player names
    LINEUP_FIELDS: Set[str] = {
        "group_name",
        "lineup",
    }

    # Fields that should be added during standardization
    METADATA_FIELDS: Set[str] = {
        "standardized_at",
        "source_endpoint",
        "data_type",
    }

    # Salary fields that need currency cleaning
    SALARY_FIELDS: Set[str] = {
        "salary",
        "adj_salary",
    }


class TableConfigs:
    """Table-specific configuration rules."""

    # Player endpoints that return player data
    PLAYER_ENDPOINTS: Set[str] = {
        "commonplayerinfo",
        "playercareerstats",
        "playerdashboardbygeneralsplits",
        "playerdashboardbygamesplits",
        "playerdashboardbyshootingsplits",
        "playerawards",
        "playergamelog",
        "draftcombinestats",
    }

    # Game endpoints
    GAME_ENDPOINTS: Set[str] = {
        "boxscoretraditionalv3",
        "boxscoreadvancedv3",
        "boxscoredefensivev2",
        "boxscorefourfactorsv3",
        "boxscorehustlev2",
        "boxscorematchupsv3",
        "boxscoremiscv3",
        "boxscorescoringv3",
        "boxscoreusagev3",
        "boxscoreplayertrackv3",
        "gamerotation",
        "playbyplayv3",
        "winprobabilitypbp",
    }

    # Season endpoints
    SEASON_ENDPOINTS: Set[str] = {
        "leaguedashlineups",
        "leaguelineupviz",
        "leaguedashopppptshot",
        "leaguedashplayerclutch",
        "leaguedashplayerptshot",
        "leaguedashplayershotlocations",
        "leaguedashplayerstats",
        "leaguedashteamclutch",
        "leaguedashteamptshot",
        "leaguedashteamshotlocations",
        "leaguedashteamstats",
        "playergamelogs",
        "leaguegamelog",
        "leaguehustlestatsplayer",
        "leaguehustlestatsteam",
        "leagueseasonmatchups",
        "playerestimatedmetrics",
        "synergyplaytypes",
        "leaguedashptstats",
        "leaguedashptdefend",
        "leaguedashptteamdefend",
    }

    # Team endpoints
    TEAM_ENDPOINTS: Set[str] = {
        "commonteamroster",
        "teamyearbyyearstats",
        "teamdashboardbygeneralsplits",
        "teamdashboardbyshootingsplits",
        "franchiseleaders",
        "franchiseplayers",
        "teamdashptpass",
        "teamplayeronoffdetails",
    }
