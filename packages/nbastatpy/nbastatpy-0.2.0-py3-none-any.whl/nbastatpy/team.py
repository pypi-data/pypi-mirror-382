from typing import List

import nba_api.stats.endpoints as nba
import pandas as pd
import requests
from bs4 import BeautifulSoup
from nba_api.stats.static import teams

from nbastatpy.standardize import standardize_dataframe
from nbastatpy.utils import Formatter, PlayTypes


class Team:
    def __init__(
        self,
        team_abbreviation: str,
        season_year: str = None,
        playoffs=False,
        permode: str = "PerGame",
    ):
        """
        Initializes a Team object.

        Parameters:
        - team_abbreviation (str): The abbreviation of the NBA team.
        - season_year (str, optional): The season year. If not provided, the current season year will be used.
        - playoffs (bool, optional): Specifies whether the team's statistics are for playoffs. Default is False.
        - permode (str, optional): The mode for the team's statistics. Default is "PerGame".

        Attributes:
        - permode (str): The formatted permode for the team's statistics.
        - season_year (str): The season year.
        - info (dict): The information about the team.
        - season (str): The formatted season.
        - season_type (str): The type of season (Regular Season or Playoffs).
        """
        self.permode = PlayTypes.PERMODE[
            permode.replace("_", "").replace("-", "").upper()
        ]
        if season_year:
            self.season_year = season_year
        else:
            self.season_year = Formatter.get_current_season_year()

        self.info = teams.find_team_by_abbreviation(team_abbreviation)

        self.season = Formatter.format_season(self.season_year)
        self.season_type = "Regular Season"
        if playoffs:
            self.season_type = "Playoffs"

        for attr_name, value in self.info.items():
            setattr(self, attr_name.lower(), self.info.get(attr_name, None))

    def get_logo(self):
        """
        Retrieves and returns the logo of the NBA team in svg format.

        Returns:
            PIL.Image.Image: The logo image of the NBA team.
        """
        pic_url = f"https://cdn.nba.com/logos/nba/{self.id}/primary/L/logo.svg"
        pic = requests.get(pic_url)
        self.logo = pic.content
        return self.logo

    def get_roster(self, standardize: bool = False) -> List[pd.DataFrame]:
        """
        Retrieves the roster of the team for the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            List[pd.DataFrame]: A list of pandas DataFrames containing the roster data.
        """
        dfs = nba.CommonTeamRoster(
            self.id,
            season=self.season,
        ).get_data_frames()

        if standardize:
            dfs = [
                standardize_dataframe(
                    df,
                    data_type="team",
                    season=self.season,
                    playoffs=(self.season_type == "Playoffs"),
                )
                for df in dfs
            ]

        self.roster = dfs
        return self.roster

    def get_salary(self) -> pd.DataFrame:
        """
        Retrieves the salary information for the team from hoopshype.com.

        Returns:
            pandas.DataFrame: A DataFrame containing the salary information for the team.
        """
        tm_name = "_".join(self.full_name.split(" ")).lower()
        year = self.season.split("-")[0]
        season_string = year + "-" + str(int(year) + 1)
        self.salary_url = f"https://hoopshype.com/salaries/{tm_name}/{season_string}/"

        result = requests.get(self.salary_url)
        soup = BeautifulSoup(result.content, features="html.parser")
        tables = soup.find_all("table")

        rows = [
            [cell.text.strip() for cell in row.find_all("td")]
            for row in tables[0].find_all("tr")
        ]

        if not rows[0]:
            rows.pop(0)
            if not rows:
                raise (ValueError(f"Season data unavailable for: {season_string}"))
        self.salary_df = pd.DataFrame(rows[1:], columns=rows[0])
        self.salary_df["Season"] = self.salary_df.columns[1].replace("/", "_")
        self.salary_df.columns = ["Player", "Salary", "Adjusted Salary", "Season"]

        return self.salary_df

    def get_year_by_year(self) -> pd.DataFrame:
        """
        Retrieves the year-by-year statistics for the team.

        Returns:
            pd.DataFrame: The year-by-year statistics for the team.
        """
        self.year_by_year = nba.TeamYearByYearStats(
            team_id=self.id, per_mode_simple=self.permode
        ).get_data_frames()[0]
        return self.year_by_year

    def get_general_splits(self) -> pd.DataFrame:
        """
        Retrieves the general splits data for the team.

        Returns:
            pd.DataFrame: The general splits data for the team.
        """
        drop_cols = [
            "TEAM_GAME_LOCATION",
            "GAME_RESULT",
            "SEASON_MONTH_NAME",
            "SEASON_SEGMENT",
            "TEAM_DAYS_REST_RANGE",
        ]
        self.general_splits = pd.concat(
            nba.TeamDashboardByGeneralSplits(
                team_id=self.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_detailed=self.permode,
            ).get_data_frames()
        ).drop(columns=drop_cols)
        return self.general_splits

    def get_shooting_splits(self) -> pd.DataFrame:
        """
        Retrieves shooting splits data for the team.

        Returns:
            pd.DataFrame: The shooting splits data for the team.
        """
        self.shooting_splits = pd.concat(
            nba.TeamDashboardByShootingSplits(
                team_id=self.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_detailed=self.permode,
            ).get_data_frames()
        )
        return self.shooting_splits

    def get_leaders(self) -> pd.DataFrame:
        """
        Retrieves the franchise leaders data for the team.

        Returns:
            pd.DataFrame: The franchise leaders data for the team.
        """
        self.leaders = nba.FranchiseLeaders(team_id=self.id).get_data_frames()[0]
        return self.leaders

    def get_franchise_players(self) -> pd.DataFrame:
        """
        Retrieves the franchise players for the team.

        Returns:
            pd.DataFrame: A DataFrame containing the franchise players' data.
        """
        self.franchise_players = nba.FranchisePlayers(
            team_id=self.id
        ).get_data_frames()[0]
        return self.franchise_players

    def get_season_lineups(self) -> pd.DataFrame:
        """
        Retrieves the season lineups for the team.

        Returns:
            pd.DataFrame: A DataFrame containing the season lineups data.
        """
        self.season_lineups = nba.LeagueDashLineups(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.season_lineups["season"] = self.season
        self.season_lineups["season_type"] = self.season_type

        return self.season_lineups

    def get_opponent_shooting(self) -> pd.DataFrame:
        """
        Retrieves the opponent shooting statistics for the team.

        Returns:
            pd.DataFrame: DataFrame containing the opponent shooting statistics.
        """
        self.opponent_shooting = nba.LeagueDashOppPtShot(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        self.opponent_shooting["season"] = self.season
        self.opponent_shooting["season_type"] = self.season_type

        return self.opponent_shooting

    def get_player_clutch(self) -> pd.DataFrame:
        """
        Retrieves the clutch statistics for the players of the team.

        Returns:
            pd.DataFrame: A DataFrame containing the clutch statistics for the players of the team.
        """
        self.player_clutch = nba.LeagueDashPlayerClutch(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.player_clutch["season"] = self.season
        self.player_clutch["season_type"] = self.season_type

        return self.player_clutch

    def get_player_shots(self) -> pd.DataFrame:
        """
        Retrieves the player shots data for the team.

        Returns:
            pd.DataFrame: The player shots data for the team.
        """
        self.player_shots = nba.LeagueDashPlayerPtShot(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        self.player_shots["season"] = self.season
        self.player_shots["season_type"] = self.season_type

        return self.player_shots

    def get_player_shot_locations(self) -> pd.DataFrame:
        """
        Retrieves the shot locations data for the players of the team.

        Returns:
            pd.DataFrame: A DataFrame containing the shot locations data for the players.
        """
        self.player_shot_locations = nba.LeagueDashPlayerShotLocations(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.player_shot_locations["season"] = self.season
        self.player_shot_locations["season_type"] = self.season_type

        return self.player_shot_locations

    def get_player_stats(self, standardize: bool = False) -> pd.DataFrame:
        """
        Retrieves the player statistics for the team.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: A DataFrame containing the player statistics.
        """
        df = nba.LeagueDashPlayerStats(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]

        df["season"] = self.season
        df["season_type"] = self.season_type

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="team",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_stats = df
        return self.player_stats

    def get_player_point_defend(self) -> pd.DataFrame:
        """
        Retrieves the player point defense data for the team.

        Returns:
            pd.DataFrame: The player point defense data for the team.
        """
        self.player_point_defend = nba.LeagueDashPtDefend(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        self.player_point_defend["season"] = self.season
        self.player_point_defend["season_type"] = self.season_type

        return self.player_point_defend

    def get_player_hustle(self) -> pd.DataFrame:
        """
        Retrieves the hustle stats for the players of the team.

        Returns:
            pd.DataFrame: A DataFrame containing the hustle stats for the players.
        """
        self.player_hustle = nba.LeagueHustleStatsPlayer(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
        ).get_data_frames()[0]
        self.player_hustle["season"] = self.season
        self.player_hustle["season_type"] = self.season_type

        return self.player_hustle

    def get_lineup_details(self) -> pd.DataFrame:
        """
        Retrieves the lineup details for the team.

        Returns:
            pd.DataFrame: The lineup details for the team.
        """
        self.lineup_details = nba.LeagueLineupViz(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            minutes_min=1,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.lineup_details["season"] = self.season
        self.lineup_details["season_type"] = self.season_type

        return self.lineup_details

    def get_player_on_details(self) -> pd.DataFrame:
        """
        Retrieves the player on-court details for the team.

        Returns:
            pd.DataFrame: A DataFrame containing the player on-court details.
        """
        self.player_on_details = nba.LeaguePlayerOnDetails(
            team_id=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.player_on_details["season"] = self.season
        self.player_on_details["season_type"] = self.season_type

        return self.player_on_details

    def get_player_matchups(self, defense=False) -> pd.DataFrame:
        """
        Retrieves player matchups for the team.

        Args:
            defense (bool, optional): If True, retrieves defensive matchups. If False, retrieves offensive matchups. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame containing player matchups for the team.
        """
        if defense:
            self.player_matchups = nba.LeagueSeasonMatchups(
                def_team_id_nullable=self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_simple=self.permode,
            ).get_data_frames()[0]
        else:
            self.player_matchups = nba.LeagueSeasonMatchups(
                off_team_id_nullable=self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_simple=self.permode,
            ).get_data_frames()[0]

        self.player_matchups["season"] = self.season
        self.player_matchups["season_type"] = self.season_type

        return self.player_matchups

    def get_player_passes(self) -> pd.DataFrame:
        """
        Retrieves the player passes data for the team.

        Returns:
            pd.DataFrame: The player passes data for the team.
        """
        self.player_passes = pd.concat(
            nba.TeamDashPtPass(
                team_id=self.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_simple=self.permode,
            ).get_data_frames()
        )

        group_cols = ["PASS_FROM", "PASS_TO"]
        self.player_passes["GROUP_SET"] = self.player_passes[group_cols].apply(
            Formatter.combine_strings, axis=1
        )
        self.player_passes = self.player_passes.drop(columns=group_cols)
        return self.player_passes.reset_index(drop=True)

    def get_player_onoff(self) -> pd.DataFrame:
        """
        Retrieves the on-off court details for the players of the team.

        Returns:
            pd.DataFrame: A DataFrame containing the on-off court details for the players.
        """
        self.player_onoff = pd.concat(
            nba.TeamPlayerOnOffDetails(
                team_id=team.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_detailed=self.permode,
            ).get_data_frames()[1:]
        )
        return self.player_onoff.reset_index(drop=True)


if __name__ == "__main__":
    team_name = "MIL"
    team = Team(team_name, season_year="2024", playoffs=True)
    print(team.get_salary())
