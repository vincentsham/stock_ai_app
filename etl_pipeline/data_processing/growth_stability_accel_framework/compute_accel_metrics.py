import pandas as pd
from etl_pipeline.utils import calculate_streak, calculate_streak_pos_neg

def calculate_acceleration(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate the difference of year-over-year growth percentages to determine acceleration.
    """
    column_name = f"{column}_yoy_pct"
    accel_column = f"{column}_accel"

    df[accel_column] = df[column_name] - df[column_name].shift(1)

    return df


def calculate_accel_count_4q(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate the count of positive acceleration periods for a specified column over the last 4 quarters.
    """
    accel_column = f"{column}_accel"
    count_column = f"{column}_accel_count_4q"

    # Create a flag for positive acceleration
    df[f"{accel_column}_positive_flag"] = (df[accel_column] > 0).astype(int)

    # Calculate count of positive acceleration over the last 4 periods
    df[count_column] = df[f"{accel_column}_positive_flag"].fillna(0).rolling(window=4, min_periods=1).sum().astype(int)

    return df

def calculate_accel_streak_length(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate the length of the current streak of positive acceleration for a specified column.
    """
    accel_column = f"{column}_accel"
    streak_column = f"{column}_accel_streak_length"

    # Create a flag for positive acceleration
    df[f"{accel_column}_positive_flag"] = (df[accel_column] > 0).astype(int)

    # Calculate streak length using the utility function
    df[streak_column] = calculate_streak(df[f"{accel_column}_positive_flag"])

    return df

def compute_accel_regime(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Compute acceleration regime based on acceleration and volatility metrics.
    """
    accel_count_column = f"{column}_accel_count_4q"
    streak_length_column = f"{column}_accel_streak_length"  
    accel_regime_column = f"{column}_accel_regime"


    # Acceleration Regime Table:
    # 0 if accel_count_4q >= 3 and streak_length >= 2 → Sustained Acceleration
    # 1 if accel_count_4q >= 3 and streak_length < 2 → Choppy Acceleration
    # 2 if accel_count_4q = 2 and streak_length = 2 → Emerging Acceleration
    # 3 if accel_count_4q = 2 and streak_length < 2 → Unstable Momentum
    # 4 if accel_count_4q < 2 → Deceleration

    df[accel_regime_column] = "Deceleration"
    df.loc[(df[accel_count_column] >= 3) & (df[streak_length_column] >= 2), accel_regime_column] = "Sustained Acceleration"
    df.loc[(df[accel_count_column] >= 3) & (df[streak_length_column] < 2), accel_regime_column] = "Choppy Acceleration"
    df.loc[(df[accel_count_column] == 2) & (df[streak_length_column] == 2), accel_regime_column] = "Emerging Acceleration"
    df.loc[(df[accel_count_column] == 2) & (df[streak_length_column] < 2), accel_regime_column] = "Unstable Momentum"
    return df
