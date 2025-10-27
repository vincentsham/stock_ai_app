import pandas as pd
from etl_pipeline.utils import calculate_streak
import numpy as np

def calculate_volatility(df: pd.DataFrame, column: str, threshold: float, ttm: bool = True) -> pd.DataFrame:
    """
    Calculate the volatility of year-over-year growth for a specified column over a rolling window.
    """
    growth_yoy_column = f"{column}_yoy_growth_pct"
    volatility_yoy_column = f"{column}_yoy_volatility_4q"
    volatility_yoy_flag_column = f"{column}_yoy_volatility_flag"
    growth_qoq_column = f"{column}_qoq_growth_pct"
    volatility_qoq_column = f"{column}_qoq_volatility_4q"
    volatility_qoq_flag_column = f"{column}_qoq_volatility_flag"
    growth_ttm_column = f"{column}_ttm_growth_pct"
    volatility_ttm_column = f"{column}_ttm_volatility_4q"
    volatility_ttm_flag_column = f"{column}_ttm_volatility_flag"

    # Calculate rolling standard deviation of YoY growth over a 4-period window excluding the current period
    # Note: if it has NaN in the window, the result will be NaN
    df[volatility_yoy_column] = df[growth_yoy_column].shift(1).rolling(window=4).std()
    df.loc[df[growth_yoy_column].isna(), volatility_yoy_column] = np.nan
    # Assign volatility flag based on threshold; NaNs remain NaN
    df[volatility_yoy_flag_column] = df[volatility_yoy_column].apply(lambda x: 0 if x < threshold else 1)
    df.loc[df[growth_yoy_column].isna(), volatility_yoy_flag_column] = np.nan


    # Calculate rolling standard deviation of QoQ growth over a 4-period window excluding the current period
    df[volatility_qoq_column] = df[growth_qoq_column].shift(1).rolling(window=4).std()
    df.loc[df[growth_qoq_column].isna(), volatility_qoq_column] = np.nan
    # Assign volatility flag based on threshold
    df[volatility_qoq_flag_column] = df[volatility_qoq_column].apply(lambda x: 0 if x < threshold else 1)
    df.loc[df[growth_qoq_column].isna(), volatility_qoq_flag_column] = np.nan

    if ttm:
        # Calculate rolling standard deviation of TTM growth over a 4-period window excluding the current period
        df[volatility_ttm_column] = df[growth_ttm_column].shift(1).rolling(window=4).std()
        df.loc[df[growth_ttm_column].isna(), volatility_ttm_column] = np.nan
        # Assign volatility flag based on threshold
        df[volatility_ttm_flag_column] = df[volatility_ttm_column].apply(lambda x: 0 if x < threshold/2 else 1)
        df.loc[df[growth_ttm_column].isna(), volatility_ttm_flag_column] = np.nan


    return df



def compute_volatility_regime(df: pd.DataFrame, column: str, ttm: bool = True) -> pd.DataFrame:
    """
    Calculate the count of volatile periods for a specified column over the last 4 quarters.
    """
    growth_yoy_column = f"{column}_yoy_growth_pct"
    volatility_yoy_column = f"{column}_yoy_volatility_4q"
    volatility_yoy_flag_column = f"{column}_yoy_volatility_flag"
    drift_yoy_column = f"{column}_yoy_growth_drift"
    outlier_yoy_flag_column = f"{column}_yoy_outlier_flag"
    regime_yoy_column = f"{column}_yoy_stability_regime"

    growth_qoq_column = f"{column}_qoq_growth_pct"
    volatility_qoq_column = f"{column}_qoq_volatility_4q"
    volatility_qoq_flag_column = f"{column}_qoq_volatility_flag"
    drift_qoq_column = f"{column}_qoq_growth_drift"
    outlier_qoq_flag_column = f"{column}_qoq_outlier_flag"
    regime_qoq_column = f"{column}_qoq_stability_regime"

    growth_ttm_column = f"{column}_ttm_growth_pct"
    volatility_ttm_column = f"{column}_ttm_volatility_4q"
    volatility_ttm_flag_column = f"{column}_ttm_volatility_flag"
    drift_ttm_column = f"{column}_ttm_growth_drift"
    outlier_ttm_flag_column = f"{column}_ttm_outlier_flag"
    regime_ttm_column = f"{column}_ttm_stability_regime"

   # Calculate drift as the mean of YoY growth over the past 4 periods excluding the current period
    df[drift_yoy_column] = df[growth_yoy_column].shift(1).rolling(window=4).mean()
    df.loc[df[growth_yoy_column].isna(), drift_yoy_column] = np.nan
    df[drift_qoq_column] = df[growth_qoq_column].shift(1).rolling(window=4).mean()
    df.loc[df[growth_qoq_column].isna(), drift_qoq_column] = np.nan


    # Identify outliers where the absolute drift exceeds the 1.5 * volatility
    df[outlier_yoy_flag_column] = df.apply(lambda x: 1 if abs(x[drift_yoy_column]) > 1.5 * x[volatility_yoy_column] else 0, axis=1)
    df[outlier_qoq_flag_column] = df.apply(lambda x: 1 if abs(x[drift_qoq_column]) > 1.5 * x[volatility_qoq_column] else 0, axis=1)

    df.loc[df[growth_yoy_column].isna(), outlier_yoy_flag_column] = np.nan
    df.loc[df[growth_qoq_column].isna(), outlier_qoq_flag_column] = np.nan


    # Determine stability regime based on volatility and outlier flags
    # if volatility is low and no outlier → Stable
    # if volatility is low and outlier → Stable but Disturbed
    # if volatility is high → Volatile
    # if volatility is low and drift < -0.02 → Structurally Deteriorating

    def get_stability_regime(volatility_flag, outlier_flag, drift) -> str:
        if np.isnan(volatility_flag) or np.isnan(outlier_flag) or np.isnan(drift):
            return np.nan
        if volatility_flag == 0:
            if outlier_flag == 0:
                if drift < -0.02:
                    return "structurally deteriorating"
                else:
                    return "stable"
            else:
                return "stable but disturbed"
        else:
            return "volatile"
    df[regime_yoy_column] = df.apply(lambda row: 
                                     get_stability_regime(row[volatility_yoy_flag_column], 
                                                          row[outlier_yoy_flag_column], 
                                                          row[drift_yoy_column]), axis=1)
    df[regime_qoq_column] = df.apply(lambda row: 
                                     get_stability_regime(row[volatility_qoq_flag_column], 
                                                          row[outlier_qoq_flag_column], 
                                                          row[drift_qoq_column]), axis=1)
    
    if ttm:
        df[drift_ttm_column] = df[growth_ttm_column].shift(1).rolling(window=4).mean()
        df.loc[df[growth_ttm_column].isna(), drift_ttm_column] = np.nan
        df[outlier_ttm_flag_column] = df.apply(lambda x: 1 if abs(x[drift_ttm_column]) > 1.5 * x[volatility_ttm_column] else 0, axis=1)
        df.loc[df[growth_ttm_column].isna(), outlier_ttm_flag_column] = np.nan
        df[regime_ttm_column] = df.apply(lambda row: 
                                        get_stability_regime(row[volatility_ttm_flag_column], 
                                                            row[outlier_ttm_flag_column], 
                                                            row[drift_ttm_column]), axis=1)

    return df

def compute_stability_metrics(df: pd.DataFrame, column: str, volatility_threshold: float, ttm: bool = True) -> pd.DataFrame:
    """
    Compute stability metrics for a specified column in the DataFrame.
    """
    df = calculate_volatility(df, column, volatility_threshold, ttm=ttm)
    df = compute_volatility_regime(df, column, ttm=ttm)
    return df