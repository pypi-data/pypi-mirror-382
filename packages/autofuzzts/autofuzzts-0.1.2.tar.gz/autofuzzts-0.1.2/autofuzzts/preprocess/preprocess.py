import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Literal


def preprocess_data(df: pd.DataFrame, diff_type: Literal['perc', 'abs'] = 'perc', scaler: MinMaxScaler = None) -> pd.DataFrame:
    """
    Prepares time series data by calculating differences, scaling, and selecting rows.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame with a single column named 'Y' containing the time series data.
        diff_type (str): Type of difference to calculate ('perc' for percentage, 'abs' for absolute). Default is 'perc'.
        n_rows (int): Number of rows to retain from the end. If -1, use all rows.
    
    Returns:
        np.ndarray: The preprocessed data, scaled and ready for further processing.
        MinMaxScaler: The scaler used for scaling, useful for inverse transformation.
    """
    
    # Step 1: Calculate the difference based on user choice
    if diff_type == 'perc':
        df['diff'] = df['Y'].pct_change()  # Percentage difference
    elif diff_type == 'abs':
        df['diff'] = df['Y'].diff()  # Absolute difference
    else:
        raise ValueError("Invalid diff_type. Choose 'perc' for percentage or 'abs' for absolute.")
    

    ## Replace infinite values with 1 or -1
    df['diff'] = np.where(df['diff'] == np.inf, 1, df['diff'])
    df['diff'] = np.where(df['diff'] == -np.inf, -1, df['diff'])

    ## If diff is bellow 0.01 quantile or 0.99 quantile, replace with 0.01 or 0.99 quantile
    df['diff'] = np.where(df['diff'] < df['diff'].quantile(0.01), df['diff'].quantile(0.01), df['diff'])
    df['diff'] = np.where(df['diff'] > df['diff'].quantile(0.99), df['diff'].quantile(0.99), df['diff'])


    ## Relace NaNs with 0
    df['diff'] = df['diff'].fillna(0)  # Replace NaNs with 0, or adjust as needed

    # Step 2: Scale only the 'diff' column
    if scaler is None:  # If no scaler is provided, create a new one (otherwise use the existing one)
        scaler = MinMaxScaler()

    df_scaled = df.copy()
    df_scaled['diff_scaled'] = scaler.fit_transform(df[['diff']])  # Scale 'diff' column only
 



    return df_scaled, scaler  # Return scaled data and scaler for possible inverse transform

def preprocess_data_val(df: pd.DataFrame,df_train: pd.DataFrame, diff_type: Literal['perc', 'abs'] = 'perc', scaler: MinMaxScaler = None):
    '''
    Attach last row of train set to the beginnig of the val set and preprocess the data. In the end remove the attached row.
    '''
    df_concat = pd.concat([df_train.tail(1), df], axis=0)
    df_preprocessed, scaler = preprocess_data(df=df_concat, diff_type=diff_type, scaler=scaler)
    df_preprocessed = df_preprocessed.iloc[1:]
    return df_preprocessed

    