import pandas as pd
import warnings


def validate_and_clean_input(df: pd.DataFrame, covariates:list[str] = None) -> pd.DataFrame:
    """
    Validates the input DataFrame, ensuring it contains at least one column.
    If the DataFrame contains multiple columns, all columns except the first 
    are removed, and a warning is issued.

    Parameters:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: A DataFrame with only the first column retained.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame.")
    
    if df.shape[1] == 0:
        raise ValueError("Input DataFrame must contain at least one column.")
    
    # If there are multiple columns, keep only the first one and warn the user
    if df.shape[1] > 1:
        if covariates is None:
            warnings.warn("Input DataFrame has multiple columns. Only the first column will be used.")
            df = df[[df.columns[0]]]
        else:
            warnings.warn("Input DataFrame has multiple columns. Covariates will be used for modelling.")
            df = df[[df.columns[0]] + covariates]
        
        

    # Standardize column name to 'Y'
    df = df.rename(columns={df.columns[0]: 'Y'})

    # Convert all selected columns to numeric and fill NaNs with 0
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    return df

