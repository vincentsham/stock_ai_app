import pandas as pd
from etl_pipeline.utils import calculate_streak, calculate_streak_pos_neg
import numpy as np

def calculate_acceleration(df: pd.DataFrame, column: str, ttm: bool = True) -> pd.DataFrame:
    """
    Calculate the difference of year-over-year growth percentages to determine acceleration.
    """
    growth_yoy_name = f"{column}_yoy_growth_pct"
    accel_yoy_column = f"{column}_yoy_accel"
    growth_qoq_name = f"{column}_qoq_growth_pct"
    accel_qoq_column = f"{column}_qoq_accel"
    growth_ttm_name = f"{column}_ttm_growth_pct"
    accel_ttm_column = f"{column}_ttm_accel"

    df[accel_yoy_column] = df[growth_yoy_name].astype(float) - df[growth_yoy_name].shift(1).astype(float)
    df[accel_qoq_column] = df[growth_qoq_name].astype(float) - df[growth_qoq_name].shift(1).astype(float)
    if ttm:
        df[accel_ttm_column] = df[growth_ttm_name].astype(float) - df[growth_ttm_name].shift(1).astype(float)

    return df


def calculate_accel_count_4q(df: pd.DataFrame, column: str, ttm: bool = True) -> pd.DataFrame:
    """
    Calculate the count of positive acceleration periods for a specified column over the last 4 quarters.
    """
    accel_yoy_column = f"{column}_yoy_accel"
    count_yoy_column = f"{column}_yoy_accel_count_4q"
    accel_yoy_flag_column = f"{column}_yoy_accel_positive_flag" 
    accel_qoq_column = f"{column}_qoq_accel"
    count_qoq_column = f"{column}_qoq_accel_count_4q"
    accel_qoq_flag_column = f"{column}_qoq_accel_positive_flag"
    accel_ttm_column = f"{column}_ttm_accel"
    count_ttm_column = f"{column}_ttm_accel_count_4q"
    accel_ttm_flag_column = f"{column}_ttm_accel_positive_flag"

    # Create a flag for positive acceleration
    df[accel_yoy_flag_column] = (df[accel_yoy_column] > 0).astype(int)
    df[accel_qoq_flag_column] = (df[accel_qoq_column] > 0).astype(int)
    
    df.loc[df[accel_yoy_column].isna(), accel_yoy_flag_column] = np.nan
    df.loc[df[accel_qoq_column].isna(), accel_qoq_flag_column] = np.nan
    

    # Calculate count of positive acceleration over the last 4 periods
    df[count_yoy_column] = df[accel_yoy_flag_column].fillna(0).rolling(window=4, min_periods=1).sum().astype(int)
    df[count_qoq_column] = df[accel_qoq_flag_column].fillna(0).rolling(window=4, min_periods=1).sum().astype(int)
    
    df.loc[df[accel_yoy_flag_column].isna(), count_yoy_column] = np.nan
    df.loc[df[accel_qoq_flag_column].isna(), count_qoq_column] = np.nan
    
    if ttm:
        df[accel_ttm_flag_column] = (df[accel_ttm_column] > 0).astype(int)
        df.loc[df[accel_ttm_column].isna(), accel_ttm_flag_column] = np.nan
        df[count_ttm_column] = df[accel_ttm_flag_column].fillna(0).rolling(window=4, min_periods=1).sum().astype(int)
        df.loc[df[accel_ttm_flag_column].isna(), count_ttm_column] = np.nan

    return df

def calculate_accel_streak_length(df: pd.DataFrame, column: str, ttm: bool = True) -> pd.DataFrame:
    """
    Calculate the length of the current streak of positive acceleration for a specified column.
    """
    accel_yoy_column = f"{column}_yoy_accel"
    streak_yoy_column = f"{column}_yoy_accel_streak_length"
    accel_yoy_flag_column = f"{column}_yoy_accel_positive_flag"
    accel_qoq_column = f"{column}_qoq_accel"
    streak_qoq_column = f"{column}_qoq_accel_streak_length"
    accel_qoq_flag_column = f"{column}_qoq_accel_positive_flag"
    accel_ttm_column = f"{column}_ttm_accel"
    streak_ttm_column = f"{column}_ttm_accel_streak_length"
    accel_ttm_flag_column = f"{column}_ttm_accel_positive_flag"


    # Calculate streak length using the utility function
    df[streak_yoy_column] = calculate_streak(df[accel_yoy_flag_column])
    df[streak_qoq_column] = calculate_streak(df[accel_qoq_flag_column])
    if ttm:
        df[streak_ttm_column] = calculate_streak(df[accel_ttm_flag_column])

    return df

def compute_accel_regime(df: pd.DataFrame, column: str, ttm: bool = True) -> pd.DataFrame:
    """
    Compute acceleration regime based on acceleration and volatility metrics.
    """
    accel_yoy_count_column = f"{column}_yoy_accel_count_4q"
    streak_yoy_length_column = f"{column}_yoy_accel_streak_length"
    accel_yoy_regime_column = f"{column}_yoy_accel_regime"
    accel_qoq_count_column = f"{column}_qoq_accel_count_4q"
    streak_qoq_length_column = f"{column}_qoq_accel_streak_length"
    accel_qoq_regime_column = f"{column}_qoq_accel_regime"
    accel_ttm_count_column = f"{column}_ttm_accel_count_4q"
    streak_ttm_length_column = f"{column}_ttm_accel_streak_length"
    accel_ttm_regime_column = f"{column}_ttm_accel_regime"


    # Acceleration Regime Table:
    # 0 if accel_count_4q >= 3 and streak_length >= 2 → Sustained Acceleration
    # 1 if accel_count_4q >= 3 and streak_length < 2 → Choppy Acceleration
    # 2 if accel_count_4q = 2 and streak_length = 2 → Emerging Acceleration
    # 3 if accel_count_4q = 2 and streak_length < 2 → Unstable Momentum
    # 4 if accel_count_4q < 2 → Deceleration
    def accel_regime_logic(accel_count, streak_length) -> str:
        if np.isnan(accel_count) or np.isnan(streak_length):
            return np.nan

        if accel_count >= 3:
            if streak_length >= 2:
                return "sustained acceleration"
            elif streak_length >= 1:
                return "choppy acceleration"
            else:
                return "break the streak"
        elif accel_count == 2:
            if streak_length == 2:
                return "emerging acceleration"
            else:
                return "unstable momentum"
        elif accel_count == 1 and streak_length == 1:
            return "unstable momentum"
        else:
            return "deceleration"

    df[accel_yoy_regime_column] = df.apply(lambda row:
                                           accel_regime_logic(row[accel_yoy_count_column], row[streak_yoy_length_column]), axis=1)
    df[accel_qoq_regime_column] = df.apply(lambda row:
                                           accel_regime_logic(row[accel_qoq_count_column], row[streak_qoq_length_column]), axis=1)
    if ttm:
        df[accel_ttm_regime_column] = df.apply(lambda row:
                                            accel_regime_logic(row[accel_ttm_count_column], row[streak_ttm_length_column]), axis=1)
    return df


def compute_accel_metrics(df: pd.DataFrame, column: str, ttm: bool = True) -> pd.DataFrame:
    """
    Compute all acceleration metrics for a specified column.
    """
    df = calculate_acceleration(df, column, ttm=ttm)
    df = calculate_accel_count_4q(df, column, ttm=ttm)
    df = calculate_accel_streak_length(df, column, ttm=ttm)
    df = compute_accel_regime(df, column, ttm=ttm)
    return df