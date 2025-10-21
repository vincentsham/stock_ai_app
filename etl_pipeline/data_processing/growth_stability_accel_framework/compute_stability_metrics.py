import pandas as pd
from etl_pipeline.utils import calculate_streak

def calculate_volatility(df: pd.DataFrame, column: str, threshold: float) -> pd.DataFrame:
    """
    Calculate the volatility of year-over-year growth for a specified column over a rolling window.
    """
    yoy_column = f"{column}_yoy_pct"
    volatility_column = f"{column}_yoy_volatility_4q"
    volatility_flag_column = f"{column}_yoy_volatility_flag"

    # Calculate rolling standard deviation of YoY growth over a 4-period window excluding the current period
    df[volatility_column] = df[yoy_column].shift(1).rolling(window=4).std()
    # Assign volatility flag based on threshold
    df[volatility_flag_column] = df[volatility_column].apply(lambda x: 0 if x < threshold else 1)


    return df



def compute_volatility_regime(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate the count of volatile periods for a specified column over the last 4 quarters.
    """
    yoy_column = f"{column}_yoy_pct"
    volatility_column = f"{column}_yoy_volatility_4q"
    volatility_flag_column = f"{column}_yoy_volatility_flag"
    drift_column = f"{column}_yoy_drift"
    outlier_flag_column = f"{column}_yoy_outlier_flag"
    regime_column = f"{column}_yoy_stability_regime"


   # Calculate drift as the mean of YoY growth over the past 4 periods excluding the current period
    df[drift_column] = df[yoy_column].shift(1).rolling(window=4).mean()

    # Identify outliers where the absolute drift exceeds the 1.5 * volatility
    df[outlier_flag_column] = df[drift_column].apply(lambda x: 1 if abs(x) > 1.5 * df[volatility_column] else 0)

    # Determine stability regime based on volatility and outlier flags
    # if volatility is low and no outlier → Stable
    # if volatility is low and outlier → Stable but Disturbed
    # if volatility is high → Volatile
    # if volatility is low and drift < -0.02 → Structurally Deteriorating

    def stability_regime(row):
        if row[volatility_flag_column] == 0:
            if row[outlier_flag_column] == 0:
                if row[drift_column] < -0.02:
                    return "Structurally Deteriorating"
                else:
                    return "Stable"
            else:
                return "Stable but Disturbed"
        else:
            return "Volatile"

    df[regime_column] = df.apply(stability_regime, axis=1)

    return df