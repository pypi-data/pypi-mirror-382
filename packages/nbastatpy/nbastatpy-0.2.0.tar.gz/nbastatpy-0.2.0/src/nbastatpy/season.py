from time import sleep

import nba_api.stats.endpoints as nba
import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.progress import track

from nbastatpy.standardize import standardize_dataframe
from nbastatpy.utils import Formatter, PlayTypes


class Season:
    def __init__(self, season_year=None, playoffs=False, permode: str = "PERGAME"):
        """
        Initialize a Season object.

        Args:
            season_year (int | str, optional): The year of the season. Can be provided in various formats:
                - 4-digit year: 2022, "2022" -> 2022-23 season
                - 2-digit year: 22, "22" -> 2022-23 season
                - Full season string: "2022-23" -> 2022-23 season
                Defaults to current season if None.
            playoffs (bool, optional): Indicates if the season is for playoffs. Defaults to False.
            permode (str, optional): The per mode for the season. Defaults to "PERGAME".
        """
        self.permode = PlayTypes.PERMODE[
            permode.replace("_", "").replace("-", "").upper()
        ]
        if season_year is not None:
            self.season_year = Formatter.normalize_season_year(season_year)
        else:
            self.season_year = Formatter.get_current_season_year()

        self.season = Formatter.format_season(self.season_year)
        self.season_type = "Regular Season"
        if playoffs:
            self.season_type = "Playoffs"

    def get_salaries(self) -> pd.DataFrame:
        """
        Retrieves the salaries of NBA players for a specific season.

        Returns:
            pd.DataFrame: A DataFrame containing the salaries of NBA players for the specified season.
        """
        year = self.season.split("-")[0]
        season_string = year + "-" + str(int(year) + 1)

        url = f"https://hoopshype.com/salaries/players/{season_string}/"
        result = requests.get(url)
        soup = BeautifulSoup(result.content, features="html.parser")
        tables = soup.find_all("table")[0]

        # # Get the table rows
        rows = [
            [cell.text.strip() for cell in row.find_all("td")]
            for row in tables.find_all("tr")
        ]

        self.salary_df = pd.DataFrame(rows[1:], columns=rows[0])
        if "" in self.salary_df.columns:
            self.salary_df = self.salary_df.drop(columns=[""])

        self.salary_df["Season"] = self.salary_df.columns[1].replace("/", "_")
        self.salary_df.columns = ["Player", "Salary", "Adj_Salary", "Season"]

        return self.salary_df

    def get_lineups(self, standardize: bool = False):
        """
        Retrieves the lineups data for the specified season, season type, and per mode.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The lineups data for the specified season, season type, and per mode.
        """
        df = nba.LeagueDashLineups(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.lineups = df
        return self.lineups

    def get_lineup_details(self, standardize: bool = False):
        """
        Retrieves the lineup details for the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The lineup details for the specified season.
        """
        df = nba.LeagueLineupViz(
            season=self.season,
            season_type_all_star=self.season_type,
            minutes_min=1,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.lineup_details = df
        return self.lineup_details

    def get_opponent_shooting(self, standardize: bool = False):
        """
        Retrieves the opponent shooting statistics for the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The opponent shooting statistics for the season.
        """
        df = nba.LeagueDashOppPtShot(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.opponent_shooting = df
        return self.opponent_shooting

    def get_player_clutch(self, standardize: bool = False):
        """
        Retrieves the player clutch data for the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The player clutch data for the specified season.
        """
        df = nba.LeagueDashPlayerClutch(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_clutch = df
        return self.player_clutch

    def get_player_shots(self, standardize: bool = False):
        """
        Retrieves the player shots data for the specified season, season type, and per mode.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The player shots data.
        """
        df = nba.LeagueDashPlayerPtShot(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_shots = df
        return self.player_shots

    def get_player_shot_locations(self, standardize: bool = False):
        """
        Retrieves the shot locations data for the players in the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: A DataFrame containing the shot locations data for the players.
        """
        df = nba.LeagueDashPlayerShotLocations(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_shot_locations = df
        return self.player_shot_locations

    def get_player_stats(self, standardize: bool = False):
        """
        Retrieves the player statistics for the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: A DataFrame containing the player statistics.
        """
        df = nba.LeagueDashPlayerStats(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_stats = df
        return self.player_stats

    def get_team_clutch(self, standardize: bool = False):
        """
        Retrieves the clutch statistics for teams in the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: A DataFrame containing the clutch statistics for teams.
        """
        df = nba.LeagueDashTeamClutch(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.team_clutch = df
        return self.team_clutch

    def get_team_shots_bypoint(self, standardize: bool = False):
        """
        Retrieves the team shots by point data for the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The team shots by point data.
        """
        df = nba.LeagueDashTeamPtShot(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.team_shots_bypoint = df
        return self.team_shots_bypoint

    def get_team_shot_locations(self, standardize: bool = False):
        """
        Retrieves the shot locations data for teams in a specific season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The shot locations data for teams.
        """
        df = nba.LeagueDashTeamShotLocations(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.team_shot_locations = df
        return self.team_shot_locations

    def get_team_stats(self, standardize: bool = False):
        """
        Retrieves the team statistics for the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: A DataFrame containing the team statistics.
        """
        df = nba.LeagueDashTeamStats(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.team_stats = df
        return self.team_stats

    def get_player_games(self, standardize: bool = False) -> pd.DataFrame:
        """
        Retrieves the player games data for the specified season, season type, and per mode.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: A DataFrame containing the player games data.
        """
        df = nba.PlayerGameLogs(
            season_nullable=self.season,
            season_type_nullable=self.season_type,
            per_mode_simple_nullable=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_games = df
        return self.player_games

    def get_team_games(self, standardize: bool = False):
        """
        Retrieves the game log for a specific team in a given season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The game log data for the team.
        """
        df = nba.LeagueGameLog(
            season=self.season,
            season_type_all_star=self.season_type,
            player_or_team_abbreviation="T",
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.team_games = df
        return self.team_games

    def get_player_hustle(self, standardize: bool = False):
        """
        Retrieves the hustle stats for players in the specified season and season type.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: A DataFrame containing the player hustle stats.
        """
        df = nba.LeagueHustleStatsPlayer(
            season=self.season,
            season_type_all_star=self.season_type,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_hustle = df
        return self.player_hustle

    def get_team_hustle(self, standardize: bool = False):
        """
        Retrieves the team hustle stats for the specified season and season type.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The team hustle stats for the specified season and season type.
        """
        df = nba.LeagueHustleStatsTeam(
            season=self.season,
            season_type_all_star=self.season_type,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.team_hustle = df
        return self.team_hustle

    def get_player_matchups(self, standardize: bool = False):
        """
        Retrieves the player matchups for the current season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The player matchups data for the current season.
        """
        df = nba.LeagueSeasonMatchups(
            season=self.season,
            season_type_playoffs=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_matchups = df
        return self.player_matchups

    def get_player_estimated_metrics(self, standardize: bool = False):
        """
        Retrieves the estimated metrics for players in the specified season and season type.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: A DataFrame containing the estimated metrics for players.
        """
        df = nba.PlayerEstimatedMetrics(
            season=self.season,
            season_type=self.season_type,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="season",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_estimated_metrics = df
        return self.player_estimated_metrics

    def get_synergy_player(
        self, play_type: str = "Transition", offensive: bool = True
    ) -> pd.DataFrame:
        """
        Retrieves synergy data for a specific play type and offensive/defensive category.

        Args:
            play_type (str, optional): The play type to retrieve synergy data for. Defaults to "Transition".
            offensive (bool, optional): Specifies whether to retrieve offensive or defensive synergy data. Defaults to True.

        Returns:
            pd.DataFrame: The synergy data as a pandas DataFrame.
        """
        self.play_type = Formatter.check_playtype(
            play_type, playtypes=PlayTypes.PLAYTYPES
        )
        if offensive:
            self.off_def = "offensive"
        else:
            self.off_def = "defensive"

        if isinstance(self.play_type, str):
            self.synergy = nba.SynergyPlayTypes(
                season=self.season,
                per_mode_simple=self.permode,
                play_type_nullable=self.play_type,
                type_grouping_nullable=self.off_def,
                player_or_team_abbreviation="P",
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):
                temp_df = nba.SynergyPlayTypes(
                    season=self.season,
                    per_mode_simple=self.permode,
                    play_type_nullable=play,
                    type_grouping_nullable=self.off_def,
                    player_or_team_abbreviation="P",
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.synergy = pd.concat(df_list)

        return self.synergy

    def get_synergy_team(
        self, play_type: str = "Transition", offensive: bool = True
    ) -> pd.DataFrame:
        """
        Retrieves synergy data for a specific play type and team.

        Args:
            play_type (str, optional): The play type to retrieve synergy data for. Defaults to "Transition".
            offensive (bool, optional): Determines whether to retrieve offensive or defensive synergy data. Defaults to True.

        Returns:
            pd.DataFrame: A DataFrame containing the synergy data.

        Raises:
            ValueError: If the play type is not valid.

        """
        self.play_type = Formatter.check_playtype(
            play_type, playtypes=PlayTypes.PLAYTYPES
        )
        if offensive:
            self.off_def = "offensive"
        else:
            self.off_def = "defensive"

        if isinstance(self.play_type, str):
            self.synergy = nba.SynergyPlayTypes(
                season=self.season,
                per_mode_simple=self.permode,
                play_type_nullable=self.play_type,
                type_grouping_nullable=self.off_def,
                player_or_team_abbreviation="T",
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):
                temp_df = nba.SynergyPlayTypes(
                    season=self.season,
                    per_mode_simple=self.permode,
                    play_type_nullable=play,
                    type_grouping_nullable=self.off_def,
                    player_or_team_abbreviation="T",
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.synergy = pd.concat(df_list)

        return self.synergy

    def get_tracking_player(
        self,
        track_type: str = "Efficiency",
    ) -> pd.DataFrame:
        """
        Retrieves tracking data for players based on the specified track type.

        Parameters:
            track_type (str): The type of tracking data to retrieve. Defaults to "Efficiency".

        Returns:
            pd.DataFrame: A DataFrame containing the tracking data for players.
        """
        self.play_type = Formatter.check_playtype(
            track_type, playtypes=PlayTypes.TRACKING_TYPES
        )

        if isinstance(self.play_type, str):
            self.tracking = nba.LeagueDashPtStats(
                season=self.season,
                per_mode_simple=self.permode,
                pt_measure_type=self.play_type,
                player_or_team="Player",
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):
                temp_df = nba.LeagueDashPtStats(
                    season=self.season,
                    per_mode_simple=self.permode,
                    pt_measure_type=play,
                    player_or_team="Player",
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.tracking = pd.concat(df_list)

        return self.tracking

    def get_tracking_team(
        self,
        track_type: str = "Efficiency",
    ) -> pd.DataFrame:
        """
        Retrieves tracking data for a specific play type and returns it as a pandas DataFrame.

        Parameters:
            track_type (str): The play type to track. Defaults to "Efficiency".

        Returns:
            pd.DataFrame: The tracking data as a pandas DataFrame.
        """
        self.play_type = Formatter.check_playtype(track_type, PlayTypes.TRACKING_TYPES)

        if isinstance(self.play_type, str):
            self.tracking = nba.LeagueDashPtStats(
                season=self.season,
                per_mode_simple=self.permode,
                pt_measure_type=self.play_type,
                player_or_team="Team",
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):
                temp_df = nba.LeagueDashPtStats(
                    season=self.season,
                    per_mode_simple=self.permode,
                    pt_measure_type=play,
                    player_or_team="Team",
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.tracking = pd.concat(df_list)

        return self.tracking

    def get_defense_player(
        self,
        defense_type: str = "Overall",
    ) -> pd.DataFrame:
        """
        Retrieves the defensive player data based on the specified defense type.

        Args:
            defense_type (str, optional): The type of defense to retrieve. Defaults to "Overall".

        Returns:
            pd.DataFrame: The defensive player data.

        """
        self.play_type = Formatter.check_playtype(
            defense_type, playtypes=PlayTypes.DEFENSE_TYPES
        )

        if isinstance(self.play_type, str):
            self.defense = nba.LeagueDashPtDefend(
                season=self.season,
                per_mode_simple=self.permode,
                defense_category=self.play_type,
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):
                temp_df = nba.LeagueDashPtDefend(
                    season=self.season,
                    per_mode_simple=self.permode,
                    defense_category=play,
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.defense = pd.concat(df_list)

        return self.defense

    def get_defense_team(
        self,
        defense_type: str = "Overall",
    ) -> pd.DataFrame:
        """
        Retrieves the defensive statistics for teams based on the specified defense type.

        Args:
            defense_type (str, optional): The type of defense to retrieve statistics for. Defaults to "Overall".

        Returns:
            pd.DataFrame: A DataFrame containing the defensive statistics for teams.
        """
        self.play_type = Formatter.check_playtype(
            defense_type, playtypes=PlayTypes.DEFENSE_TYPES
        )

        if isinstance(self.play_type, str):
            self.defense = nba.LeagueDashPtTeamDefend(
                season=self.season,
                per_mode_simple=self.permode,
                defense_category=self.play_type,
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):
                temp_df = nba.LeagueDashPtTeamDefend(
                    season=self.season,
                    per_mode_simple=self.permode,
                    defense_category=play,
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.defense = pd.concat(df_list)

        return self.defense


if __name__ == "__main__":
    seas = Season(season_year="2004")
    print(seas.permode)
    print(seas.get_salaries())
