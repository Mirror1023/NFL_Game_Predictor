########## data_preparation.py ##########


### LIBRARY/DATA IMPORT ###   ### LIBRARY/DATA IMPORT ###   ### LIBRARY/DATA IMPORT ###   


import pandas as pd
import numpy as np
from typing import List

from src.paths import DATA_DIR

def load_csv_data_from_disk(file_name: str) -> pd.DataFrame:
    """
    Loads CSV file that the scraper previously generated and saved locally
    to disk

    Args:
        file_name (str): name of the CSV file (not the path, just the name)

    Returns:
        pd.DataFrame: 
    """
    return pd.read_csv(DATA_DIR / file_name)


### DATA CLEANSING ###   ### DATA CLEANSING ###   ### DATA CLEANSING ###   


def fix_opponent_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Some teams have changed their name and/or location, which created another
    opponent. Manually replacing team names.

    Args:
        data (pd.DataFrame): original data

    Returns:
        pd.DataFrame: fixed data
    """
    df.loc[df["opp"] == "Washington Redskins", "opp"] = "Washington Commanders"
    df.loc[df["opp"] == "Washington Football Team", "opp"] = "Washington Commanders"
    df.loc[df["opp"] == "Oakland Raiders", "opp"] = "Las Vegas Raiders"
    df.loc[df["opp"] == "Los Angeles Raiders", "opp"] = "Las Vegas Raiders"
    df.loc[df["opp"] == "Houston Oilers", "opp"] = "Tennessee Titans"
    df.loc[df["opp"] == "Tennessee Oilers", "opp"] = "Tennessee Titans"
    df.loc[df["opp"] == "San Diego Chargers", "opp"] = "Los Angeles Chargers"
    df.loc[df["opp"] == "St. Louis Rams", "opp"] = "Los Angeles Rams"

    # verifying that there are only 32 teams in the df.opp column now.
    assert len(df.opp.unique()) == 32, "There should be 32 teams in the `opp` column"
    
    return df


def map_team_abbreviations_to_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Maps the `team` column abbreviaton to the full name of the team
        Example: "ARZ" -> "Arizona Cardinals"

    Args:
        df (pd.DataFrame): original dataframe with team abbreviations

    Returns:
        pd.DataFrame: transformed dataframe with complete `team` names
    """

    MAP_ABBREVIATIONS_TO_NAMES  = {
        "ARZ": "Arizona Cardinals",
        "ATL": "Atlanta Falcons",
        "BAL": "Baltimore Ravens",
        "BUF": "Buffalo Bills",
        "CAR": "Carolina Panthers",
        "CHI": "Chicago Bears",
        "CIN": "Cincinnati Bengals",
        "CLE": "Cleveland Browns",
        "DAL": "Dallas Cowboys",
        "DEN": "Denver Broncos",
        "DET": "Detroit Lions",
        "GB": "Green Bay Packers",
        "HOU": "Houston Texans",
        "IND": "Indianapolis Colts",
        "JAX": "Jacksonville Jaguars",
        "KC": "Kansas City Chiefs",
        "LV": "Las Vegas Raiders",
        "LAC": "Los Angeles Chargers",
        "LAR": "Los Angeles Rams",
        "MIA": "Miami Dolphins",
        "MIN": "Minnesota Vikings",
        "NE": "New England Patriots",
        "NO": "New Orleans Saints",
        "NYG": "New York Giants",
        "NYJ": "New York Jets",
        "PHI": "Philadelphia Eagles",
        "PIT": "Pittsburgh Steelers",
        "SF": "San Francisco 49ers",
        "SEA": "Seattle Seahawks",
        "TB": "Tampa Bay Buccaneers",
        "TEN": "Tennessee Titans",
        "WAS": "Washington Commanders"
    }
    df.replace({"team": MAP_ABBREVIATIONS_TO_NAMES}, inplace=True)
    
    # verifying that there are only 32 teams in the df.opp column now.
    assert len(df.team.unique()) == 32, "There should be 32 teams in the `opp` column"
    
    return df


def add_home_or_away_column(data: pd.DataFrame) -> pd.DataFrame:
    """Adds a new column `home_or_away` to the dataframe with values 'HOME' or
    'AWAY'.

    Args:
        data (pd.DataFrame): original dataframe

    Returns:
        pd.DataFrame: transformed dataframe including new column `home_or_away`
    """
    
    # organizing teams by conference since the Super Bowl home/away teams are selected this way
    afc = ['Baltimore Ravens', 'Buffalo Bills', 'Cincinnati Bengals', 'Cleveland Browns', 'Denver Broncos', 'Houston Texans', 
           'Indianapolis Colts', 'Jacksonville Jaguars', 'Kansas City Chiefs', 'Las Vegas Raiders','Los Angeles Chargers', 
           'Miami Dolphins', 'New England Patriots', 'New York Jets', 'Pittsburgh Steelers', 'Tennessee Titans']

    nfc = ['Arizona Cardinals', 'Atlanta Falcons', 'Carolina Panthers', 'Chicago Bears', 'Dallas Cowboys', 'Detroit Lions',
           'Green Bay Packers', 'Los Angeles Rams', 'Minnesota Vikings', 'New Orleans Saints', 'New York Giants',
           'Philadelphia Eagles', 'San Francisco 49ers', 'Seattle Seahawks', 'Tampa Bay Buccaneers', 'Washington Commanders']
    
    #data['home_or_away'] = ['AWAY' if x == '@' else 'HOME' for x in data['@']] # original code
    
    data['home_or_away'] = np.where(data['@'] == '@', 'AWAY', 
                                np.where((data['@'] == 'N') & (data['season'] % 2 == 1) & (data['team'].isin(nfc)), 'HOME', 
                                         np.where((data['@'] == 'N') & (data['season'] % 2 == 0) & (data['team'].isin(afc)), 'HOME', 
                                                  np.where((data['@'] == 'N') & (data['season'] % 2 == 1) & (data['team'].isin(afc)), 'AWAY',
                                                           np.where((data['@'] == 'N') & (data['season'] % 2 == 0) & (data['team'].isin(nfc)), 'AWAY',
                                                                    'HOME')))))
    
    return data


def add_datetime_column(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a new column `date_time` to the dataframe with values in the format: 
    1994-09-04 16:00:00

    Args:
        data (pd.DataFrame): original dataframe

    Returns:
        pd.DataFrame: transformed dataframe including new column `date_time`
    """

    # month and day
    df[['month', 'day']] = df['date'].str.split(' ', expand=True)
    # Convert the 'day' column to integer type
    df['day'] = df['day'].astype(int)

    # Convert the `month` from string to integer
    MONTH_MAP = {
        "January":1, "February":2, "March":3, "April":4, "May":5, "June":6,
        "July":7, "August":8, "September":9, "October":10, "November":11,
        "December":12}
    df = df.replace({"month": MONTH_MAP})
    
    # Year
    df['year'] = df['season']
    df.loc[(df['month'] == 1) | (df['month'] == 2), 'year'] = df['year'] + 1

    # Extract the hour from the 'time' column
    df['hour'] = df['time'].str[0].astype(int)
    # Add 12 to the 'hour' column for times in the PM
    df['hour'] += df['time'].str.contains('PM').astype(int) * 12

    # combine year, month, day and hour to build the complete date_time
    df['date_time'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])

    # df.drop(columns=['year', 'month', 'hour', 'day'], inplace=True)

    return df


def sort_data_by_team_and_datetime(data: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts the data by team and datetime
    """
    return data.sort_values(by=['team', 'date_time'], ascending=[True, True], ignore_index=True)#.reset_index(drop=True)


### FEATURE ENGINEERING ###   ### FEATURE ENGINEERING ###   ### FEATURE ENGINEERING ###


def add_win_rates_last_n_games(
    data: pd.DataFrame,
    n_games: List[int] = [1, 3, 5]
    ) -> pd.DataFrame:
    """Adds a column for the win rate in the last N games played by a team, where N is specified in the n_games parameter.
    The function sorts the input DataFrame by team and datetime, adds a column for the win/loss result as an integer, 
    and then calculates the win rate in the last N games using a rolling window. 
    The output DataFrame includes the added columns for win rate in the last N games, as well as the original input columns.

    Args:
        data (pd.DataFrame): a DataFrame with columns 'team', 'opp', 'date_time', and 'result'
        n_matches (List[int]): a list of integers specifying the number of previous matches to calculate win rate for (default is [1, 3, 5])

    Returns:
        pd.DataFrame: a DataFrame with added columns for win rate in the last N matches played by each team, 
        where N is specified in the n_matches parameter.
    """
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)

    # add a column with the win/loss result as an integer: win = 1, loss = 0
    data['win'] = data['result'].apply(lambda x: 1 if x == 'W' else 0) 
    
    for n in n_games:
        data[f'win_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['win']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_passing_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the passing rate of each team in the last N games, where N is
        specified by the `n_games` parameter. The passing rate is calculated as the rolling average of the 
        yards gained through passes by each team in the previous N games.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the passing rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the passing rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'pass_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['passyd']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )
    
    return data


def add_rushing_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the rushing rate of each team in the last N games, where N is
        specified by the `n_games` parameter. The rushing rate is calculated as the rolling average of the 
        yards gained through rushing by each team in the previous N games.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the rushing rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the rushing rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'rush_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['rushyd']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_passing_allowed_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the passing allowed rate for each team in the last N games, where N is
        specified by the `n_games` parameter. The passing allowed rate is calculated as the rolling average of the 
        yards allowed through passing by each team in the previous N games.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the passing allowed rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the passing allowed rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'pass_allowed_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['passyd_allowed']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_rushing_allowed_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the rushing allowed rate for each team in the last N games, where N is
        specified by the `n_games` parameter. The rushing allowed rate is calculated as the rolling average of the 
        yards allowed through rushing by each team in the previous N games.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the rushing allowed rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the rushing allowed rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'rush_allowed_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['rushyd_allowed']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_ot_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the overtime (ot) rate for each team in the last N games, where N is
        specified by the `n_games` parameter. The ot rate is calculated as the rolling average of overtime games 
        played by each team in the previous N games.
        Also converts the ot column into binary integers before calculating the rates.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the overtime rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the overtime rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """

    # converts values for column "ot" (overtime) to binary integers
    data.loc[data["ot"] == "OT", "ot"] = 1
    data['ot'] = data['ot'].fillna(0) # for the remaining NaN values
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'ot_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['ot']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_to_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the turnover (to) rate for each team in the last N games, where N is
        specified by the `n_games` parameter. The to rate is calculated as the rolling average of turnovers 
        committed by each team in the previous N games.
        Also converts the NaN values of the to column into a 0 integer before calculating the rates.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the turnover rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the turnover rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """   
    
    # convert NaN values for column "to" (turnovers) into a 0 integer
    data['to'] = data['to'].fillna(0)
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'to_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['to']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_to_forced_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the turnovers forced (to_forced) rate for each team in the last N games, 
        where N is specified by the `n_games` parameter. The to_forced rate is calculated as the rolling average of 
        turnovers forced by each team in the previous N games.
        Also converts the NaN values of the to_forced column into a 0 integer before calculating the rates.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the turnovers forced rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the turnovers forced rates 
        for the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """   

    # convert NaN values for column "to_forced" (turnovers_forced) into a 0 integer
    data['to_forced'] = data['to_forced'].fillna(0)
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'to_forced_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['to_forced']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_points_scored_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the points scored rate of each team in the last N games, where N is
        specified by the `n_games` parameter. The points scored rate is calculated as the rolling average of the 
        points scored by each team in the previous N games.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the points scored rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the points scored rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'points_scored_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['points_scored']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_points_allowed_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the points allowed rate of each team in the last N games, where N is
        specified by the `n_games` parameter. The points allowed rate is calculated as the rolling average of the 
        points allowed by each team in the previous N games.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the points allowed rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the points allowed rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'points_allowed_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['points_allowed']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_1st_down_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the 1st down rate of each team in the last N games, where N is
        specified by the `n_games` parameter. The 1st down rate is calculated as the rolling average of the 
        1st downs gained by each team in the previous N games.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the 1st down rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the 1st down rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'1st_downs_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['1st_downs']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


def add_1st_down_allowed_rates_last_n_games(
    data: pd.DataFrame, 
    n_games: List[int] = [1, 3, 5] 
    ) -> pd.DataFrame:
    """ Add a column to a DataFrame indicating the 1st down allowed rate of each team in the last N games, where N is
        specified by the `n_games` parameter. The 1st down allowed rate is calculated as the rolling average of the 
        1st downs gained by each team in the previous N games.

    Args:
        data (pd.DataFrame): original dataframe
        n_games (List[int], optional): A list of integers representing the number 
        of previous games for which the 1st down allowed rate will be calculated. Default is [1, 3, 5].

    Returns:
        pd.DataFrame: A DataFrame with the same columns as the input DataFrame, 
        as well as additional columns representing the 1st down allowed rates for 
        the specified number of previous games for each team. 
        The DataFrame is sorted by team and datetime.
    """
    
    # make sure the data is sorted by team and datetime
    data = sort_data_by_team_and_datetime(data)
    
    for n in n_games:
        data[f'1st_downs_allowed_rate_last_{n}_games'] = (
            data
            .groupby(['team', 'season'])['1st_downs_allowed']
            .shift(1) # so we only use past games to avoid data leakage
            .rolling(n, min_periods=n).mean()
            .reset_index(drop=True)
        )

    return data


### DATA EXPORTATION ###   ### DATA EXPORTATION ###   ### DATA EXPORTATION ###   


def export_transformed_data_to_csv(game_level_data: pd.DataFrame):
    """
    Exports a CSV file that the scraper previously generated and that was transformed
    in 03_data_prep.ipynb.

    Args:
        game_level_data (pd.DataFrame): name of the df

    Returns:
        CSV file: 
    """
    
    # using pandas to convert the dataframe into a csv file.
    return game_level_data.to_csv("Data/transformed.csv", index=False)

