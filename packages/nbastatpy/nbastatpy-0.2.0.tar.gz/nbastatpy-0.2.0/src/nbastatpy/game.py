from typing import List

import nba_api.stats.endpoints as nba
import pandas as pd

from nbastatpy.standardize import standardize_dataframe
from nbastatpy.utils import Formatter


class Game:
    def __init__(self, game_id: str):
        """This represents a game.  Given an ID, you can get boxscore (and other) information through one of the 'get' methods

        Args:
            game_id (str): string with 10 digits
        """
        self.game_id = Formatter.format_game_id(game_id)

    def get_boxscore(self, standardize: bool = False) -> List[pd.DataFrame]:
        """Gets traditional boxscore

        Args:
            standardize: Whether to apply data standardization

        Returns:
            List[pd.DataFrame]: list of dataframes (players, starters/bench, team)
        """
        dfs = nba.BoxScoreTraditionalV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.boxscore = dfs
        return self.boxscore

    def get_advanced(self, standardize: bool = False):
        """
        Retrieves the advanced box score data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The advanced box score data for the game.
        """
        dfs = nba.BoxScoreAdvancedV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.adv_box = dfs
        return self.adv_box

    def get_defense(self, standardize: bool = False):
        """
        Retrieves the defensive statistics for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            def_box (pandas.DataFrame): DataFrame containing the defensive statistics.
        """
        dfs = nba.BoxScoreDefensiveV2(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.def_box = dfs
        return self.def_box

    def get_four_factors(self, standardize: bool = False):
        """
        Retrieves the four factors data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The four factors data for the game.
        """
        dfs = nba.BoxScoreFourFactorsV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.four_factors = dfs
        return self.four_factors

    def get_hustle(self, standardize: bool = False) -> List[pd.DataFrame]:
        """Gets hustle data for a given game

        Args:
            standardize: Whether to apply data standardization

        Returns:
            List[pd.DataFrame]: list of two dataframes (players, teams)
        """
        dfs = nba.BoxScoreHustleV2(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.hustle = dfs
        return self.hustle

    def get_matchups(self, standardize: bool = False):
        """
        Retrieves the matchups for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The matchups data for the game.
        """
        dfs = nba.BoxScoreMatchupsV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.matchups = dfs
        return self.matchups

    def get_misc(self, standardize: bool = False):
        """
        Retrieves miscellaneous box score data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The miscellaneous box score data.
        """
        dfs = nba.BoxScoreMiscV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.misc = dfs
        return self.misc

    def get_scoring(self, standardize: bool = False):
        """
        Retrieves the scoring data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The scoring data for the game.
        """
        dfs = nba.BoxScoreScoringV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.scoring = dfs
        return self.scoring

    def get_usage(self, standardize: bool = False) -> List[pd.DataFrame]:
        """Gets usage data for a given game

        Args:
            standardize: Whether to apply data standardization

        Returns:
            List[pd.DataFrame]: list of two dataframes (players, teams)
        """
        dfs = nba.BoxScoreUsageV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.usage = dfs
        return self.usage

    def get_playertrack(self, standardize: bool = False):
        """
        Retrieves the player tracking data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            playertrack (pandas.DataFrame): The player tracking data for the game.
        """
        dfs = nba.BoxScorePlayerTrackV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.playertrack = dfs
        return self.playertrack

    def get_rotations(self, standardize: bool = False):
        """
        Retrieves the rotations data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The rotations data for the game.
        """
        df = pd.concat(nba.GameRotation(game_id=self.game_id).get_data_frames())

        if standardize:
            df = standardize_dataframe(df, data_type="game")

        self.rotations = df
        return self.rotations

    def get_playbyplay(self, standardize: bool = False) -> pd.DataFrame:
        """
        Retrieves the play-by-play data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: The play-by-play data as a pandas DataFrame.
        """
        df = nba.PlayByPlayV3(self.game_id).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(df, data_type="game")

        self.playbyplay = df
        return self.playbyplay

    def get_win_probability(self, standardize: bool = False) -> pd.DataFrame:
        """
        Retrieves the win probability data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: The win probability data as a pandas DataFrame.
        """
        df = nba.WinProbabilityPBP(game_id=self.game_id).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(df, data_type="game")

        self.win_probability = df
        return self.win_probability


if __name__ == "__main__":
    GAME_ID = "0022301148"
    game = Game(game_id=GAME_ID)
    print(game.get_win_probability())
