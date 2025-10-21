import pandas as pd
from etl_pipeline.utils import calculate_streak

def calculate_yoy_growth(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate year-over-year growth for a specified column. Assumes data is sorted ascendingly by time.
    4 periods ago is used for comparison.
    """
    column_name = f"{column}_yoy_pct"
    # Handle division by zero or NaNs for calculating YoY growth
    df[column_name] = (df[column]/df[column].shift(4)) - 1

    flag_column = f"{column}_yoy_positive_flag"
    df[flag_column] = (df[column_name] > 0).astype(int)

    return df


def calculate_yoy_count_4q(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate the count of positive year-over-year growth periods for a specified column over the last 4 quarters.
    """
    flag_column = f"{column}_yoy_positive_flag"
    count_column = f"{column}_yoy_count_4q"

    # Calculate count of positive YoY growth over the last 4 periods
    df[count_column] = df[flag_column].fillna(0).rolling(window=4, min_periods=1).sum().astype(int)

    return df


def calculate_streak_length(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate the length of the current streak of positive values for a specified column.
    """
    flag_column = f"{column}_yoy_positive_flag"
    streak_column = f"{column}_yoy_streak_length"

    df[streak_column] = calculate_streak(df[flag_column], on_value=1)

    return df


def calculate_yoy_growth_flag(df: pd.DataFrame, column: str, score_regime: list[float]) -> pd.DataFrame:
    """
    Calculate a boolean flag indicating whether year-over-year growth is positive for a specified column.
    """
    yoy_column = f"{column}_yoy_pct"
    flag_column = f"{column}_yoy_growth_flag"

    # 0 if YoY growth < score_regime[0], (Deep contraction)
    # 1 if between score_regime[0] and score_regime[1], (Mild contraction)
    # 2 if between score_regime[1] and score_regime[2], (Moderate growth)
    # 3 if between score_regime[2] and score_regime[3], (Strong growth)
    # 4 if greater than or equal to score_regime[3], (Very strong growth)
    df[flag_column] = "Deep contraction"
    df.loc[(df[yoy_column] >= score_regime[0]), flag_column] = "Mild contraction"
    df.loc[(df[yoy_column] >= score_regime[1]), flag_column] = "Moderate growth"
    df.loc[(df[yoy_column] >= score_regime[2]), flag_column] = "Strong growth"
    df.loc[(df[yoy_column] >= score_regime[3]), flag_column] = "Very strong growth"

    return df


def compute_growth_regime(df: pd.DataFrame, column: str, score_regime: list[float]) -> pd.DataFrame:
    """
    Compute growth regimes for a specified column.
    """
    # 0 if growth_count_4q >= 3 and growth_streak_len >= 3 -> "Sustained Expansion"
    # 1 if growth_count_4q >= 3 and growth_streak_len < 3 -> "Developing Expansion"
    # 2 if growth_count_4q == 2 -> "Volatile Transition"
    # 3 if growth_count_4q <= 1 and growth_streak_len <= 1 -> "Tentative Turnaround"
    # 4 if growth_count_4q == 0 and growth_streak_len == 0 -> "Persistent Contraction"
    count_column = f"{column}_yoy_count_4q"
    streak_column = f"{column}_yoy_streak_length"
    regime_column = f"{column}_growth_regime"

    df[regime_column] = "Persistent Contraction"
    df.loc[(df[count_column] >= 3) & (df[streak_column] >= 3), regime_column] = "Sustained Expansion"
    df.loc[(df[count_column] >= 3) & (df[streak_column] < 3), regime_column] = "Developing Expansion"
    df.loc[(df[count_column] == 2), regime_column] = "Volatile Transition"
    df.loc[(df[count_column] <= 1) & (df[streak_column] <= 1), regime_column] = "Tentative Turnaround"

    return df
