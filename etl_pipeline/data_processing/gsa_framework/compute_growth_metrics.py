import pandas as pd
from etl_pipeline.utils import calculate_streak, calculate_pct_change
import numpy as np

def calculate_growth(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate year-over-year growth for a specified column. Assumes data is sorted ascendingly by time.
    4 periods ago is used for comparison.
    """

    
    column_yoy_name = f"{column}_yoy_growth_pct"
    column_qoq_name = f"{column}_qoq_growth_pct"
    column_ttm_name = f"{column}_ttm_growth_pct"
    column_lag_1 = f"{column}_lag_1"
    column_lag_4 = f"{column}_lag_4"
    column_ttm = f"{column}_ttm"
    column_ttm_lag_4 = f"{column}_ttm_lag_4"

    df[column_lag_1] = df[column].shift(1)
    df[column_lag_4] = df[column].shift(4)
    df[column_ttm] = df[column].rolling(window=4).sum()
    df[column_ttm_lag_4] = df[column_ttm].shift(4)


    # Handle division by zero or NaNs for calculating YoY growth
    df[column_yoy_name] = df.apply(lambda x: calculate_pct_change(x[column], x[column_lag_4]), axis=1)
    df[column_qoq_name] = df.apply(lambda x: calculate_pct_change(x[column], x[column_lag_1]), axis=1)
    df[column_ttm_name] = df.apply(lambda x: calculate_pct_change(x[column_ttm], x[column_ttm_lag_4]), axis=1)
    # Drop intermediate columns
    df.drop(columns=[column_lag_1, column_lag_4, column_ttm, column_ttm_lag_4], inplace=True)


    # Create flags for positive growth; 1 if positive or zero, 0 if negative, NaN remains NaN
    def get_positive_flag(value: float) -> int:
        if pd.isna(value):
            return np.nan
        elif value > 0:
            return 1
        else:
            return 0

    flag_yoy_column = f"{column}_yoy_positive_flag"
    df[flag_yoy_column] = df[column_yoy_name].apply(get_positive_flag)

    flag_qoq_column = f"{column}_qoq_positive_flag"
    df[flag_qoq_column] = df[column_qoq_name].apply(get_positive_flag)

    flag_ttm_column = f"{column}_ttm_positive_flag"
    df[flag_ttm_column] = df[column_ttm_name].apply(get_positive_flag)

    return df


def calculate_count_4q(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate the count of positive year-over-year growth periods for a specified column over the last 4 quarters.
    """
    flag_yoy_column = f"{column}_yoy_positive_flag"
    count_yoy_column = f"{column}_yoy_count_4q"
    flag_qoq_column = f"{column}_qoq_positive_flag"
    count_qoq_column = f"{column}_qoq_count_4q"
    flag_ttm_column = f"{column}_ttm_positive_flag"
    count_ttm_column = f"{column}_ttm_count_4q"

    # Calculate count of positive YoY growth over the last 4 periods
    # output NaN if one of the 4 periods is NaN
    df[count_yoy_column] = df[flag_yoy_column].rolling(window=4, min_periods=4).apply(lambda x: x.sum() if not x.isnull().any() else np.nan, raw=False)
    # Calculate count of positive QoQ growth over the last 4 periods
    df[count_qoq_column] = df[flag_qoq_column].rolling(window=4, min_periods=1).apply(lambda x: x.sum() if not x.isnull().any() else np.nan, raw=False)
    # Calculate count of positive TTM growth over the last 4 periods
    df[count_ttm_column] = df[flag_ttm_column].rolling(window=4, min_periods=1).apply(lambda x: x.sum() if not x.isnull().any() else np.nan, raw=False)

    return df


def calculate_streak_length(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate the length of the current streak of positive values for a specified column.
    """
    flag_yoy_column = f"{column}_yoy_positive_flag"
    streak_yoy_column = f"{column}_yoy_streak_length"
    flag_qoq_column = f"{column}_qoq_positive_flag"
    streak_qoq_column = f"{column}_qoq_streak_length"
    flag_ttm_column = f"{column}_ttm_positive_flag"
    streak_ttm_column = f"{column}_ttm_streak_length"

    df[streak_yoy_column] = calculate_streak(df[flag_yoy_column], on_value=1)
    df[streak_qoq_column] = calculate_streak(df[flag_qoq_column], on_value=1)
    df[streak_ttm_column] = calculate_streak(df[flag_ttm_column], on_value=1)

    return df


def calculate_yoy_growth_flag(df: pd.DataFrame, column: str, score_regime: list[float]) -> pd.DataFrame:
    """
    Calculate a boolean flag indicating whether year-over-year growth is positive for a specified column.
    """
    column_yoy_name = f"{column}_yoy_growth_pct"
    class_yoy_column = f"{column}_yoy_growth_class"
    column_qoq_name = f"{column}_qoq_growth_pct"
    class_qoq_column = f"{column}_qoq_growth_class"
    column_ttm_name = f"{column}_ttm_growth_pct"
    class_ttm_column = f"{column}_ttm_growth_class"

    # 0 if YoY growth < score_regime[0], (Deep contraction)
    # 1 if between score_regime[0] and score_regime[1], (Mild contraction)
    # 2 if between score_regime[1] and score_regime[2], (Moderate growth)
    # 3 if between score_regime[2] and score_regime[3], (Strong growth)
    # 4 if greater than or equal to score_regime[3], (Very strong growth)
    def get_growth_class(value: float) -> str:
        if pd.isna(value):
            return None
        elif value < score_regime[0]:
            return "Deep contraction"
        elif value < score_regime[1]:
            return "Mild contraction"
        elif value < score_regime[2]:
            return "Moderate growth"
        elif value < score_regime[3]:
            return "Strong growth"
        else:
            return "Very strong growth"
    df[class_yoy_column] = df[column_yoy_name].apply(get_growth_class)
    df[class_qoq_column] = df[column_qoq_name].apply(get_growth_class)
    df[class_ttm_column] = df[column_ttm_name].apply(get_growth_class)

    return df


def compute_growth_regime(df: pd.DataFrame, column: str, score_regime: list[float]) -> pd.DataFrame:
    """
    Compute growth regimes for a specified column.
    """
    count_yoy_column = f"{column}_yoy_count_4q"
    streak_yoy_column = f"{column}_yoy_streak_length"
    regime_yoy_column = f"{column}_yoy_growth_regime"
    count_qoq_column = f"{column}_qoq_count_4q"
    streak_qoq_column = f"{column}_qoq_streak_length"
    regime_qoq_column = f"{column}_qoq_growth_regime"
    count_ttm_column = f"{column}_ttm_count_4q"
    streak_ttm_column = f"{column}_ttm_streak_length"
    regime_ttm_column = f"{column}_ttm_growth_regime"

    # 0 if growth_count_4q >= 3 and growth_streak_len >= 3 -> "Sustained Expansion"
    # 1 if growth_count_4q >= 3 and growth_streak_len < 3 -> "Developing Expansion"
    # 2 if growth_count_4q == 2 -> "Volatile Transition"
    # 3 if growth_count_4q <= 1 and growth_streak_len <= 1 -> "Tentative Turnaround"
    # 4 if growth_count_4q == 0 and growth_streak_len == 0 -> "Persistent Contraction"
    def get_growth_regime(value_count: int, value_streak: int) -> str:
        if pd.isna(value_count) or pd.isna(value_streak):
            return None
        elif value_count >= 3 and value_streak >= 3:
            return "Sustained Expansion"
        elif value_count >= 3 and 1 <= value_streak < 3:
            return "Developing Expansion"
        elif value_count >= 3 and value_streak == 0:
            return "Break the Streak"
        elif value_count == 2:
            return "Volatile Transition"
        elif value_count == 1 and value_streak == 1:
            return "Tentative Turnaround"
        elif value_count <= 1 and value_streak == 0:
            return "Persistent Contraction"

    df[regime_yoy_column] = df.apply(lambda x: get_growth_regime(x[count_yoy_column], x[streak_yoy_column]), axis=1)
    df[regime_qoq_column] = df.apply(lambda x: get_growth_regime(x[count_qoq_column], x[streak_qoq_column]), axis=1)
    df[regime_ttm_column] = df.apply(lambda x: get_growth_regime(x[count_ttm_column], x[streak_ttm_column]), axis=1)

    return df  


def compute_growth_metrics(df: pd.DataFrame, column: str, score_regime: list[float]) -> pd.DataFrame:
    """
    Compute all growth metrics for a specified column.
    """
    df = calculate_growth(df, column)
    df = calculate_count_4q(df, column)
    df = calculate_streak_length(df, column)
    df = calculate_yoy_growth_flag(df, column, score_regime)
    df = compute_growth_regime(df, column, score_regime)
    return df