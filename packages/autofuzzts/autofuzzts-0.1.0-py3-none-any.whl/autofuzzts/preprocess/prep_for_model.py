import pandas as pd
import warnings
from sklearn.preprocessing import LabelEncoder

def prepare_for_model(df: pd.DataFrame, number_of_lags: int):
    """
    Prepare clustering data for modeling.
    
    Parameters:
    - df (pd.DataFrame): The input DataFrame containing clustering data.
    - number_of_lags (int): The number of lag features to create.

    Returns:
    - X_train (pd.DataFrame): Features for training the model.
    - y_train (np.ndarray): Target variable for training the model.
    """
    
    # Prepare the 'cluster' column
    df.loc[:, "cluster"] = df["cluster"].str.replace("set_", "").astype(int).copy()

    # Create lagged features
    for i in range(1, number_of_lags + 1):
        df.loc[:, "cluster_lag" + str(i)] = df["cluster"].shift(i).copy()
        df.loc[:, "membership_value_lag" + str(i)] = df["membership_value"].shift(i).copy()
        df.loc[:, "left_lag" + str(i)] = df["left"].shift(i).copy()

    # Reset warning filter
    warnings.filterwarnings("default", category=pd.errors.SettingWithCopyWarning)

    # Prepare the model DataFrame
    df_model = df.copy()
    df_model.drop(columns=["membership_value", "left"], inplace=True)
    df_model.rename(columns={"X_value": "Y"}, inplace=True)

    numeric_cols = df_model.select_dtypes(include=['float64', 'int64']).columns
    df_model[numeric_cols] = df_model[numeric_cols].fillna(0)


    # Separate target and features
    y_train = df_model["cluster"]
    X_train = df_model.drop(columns=["Y", "cluster"])

    # Encode categorical columns
    label_encoder = LabelEncoder()
    encoded_cols = []

    # Loop through columns and encode if they start with 'cluster_'
    for col in X_train.columns:
        if col.startswith("cluster_"):
            X_train[col] = label_encoder.fit_transform(X_train[col])
            encoded_cols.append(col)

    # Label encode y_train
    y_train = label_encoder.fit_transform(y_train)

    return X_train, y_train

def prepare_for_model_val_set(df_val_fp: pd.DataFrame, df_train_fp: pd.DataFrame, n_lags: pd.DataFrame):
    '''
    Prepare validation set. Attach to the begginning of val set rows from the end of the train set (based on numbef of lags). In the end remove the attached rows.
    '''
    df_concat = pd.concat([df_train_fp.tail(n_lags), df_val_fp], axis=0).reset_index(drop=True)


    X_val, y_val = prepare_for_model(df=df_concat, number_of_lags=n_lags)

    X_val = X_val.iloc[n_lags:]
    y_val = y_val[n_lags:]

    return X_val, y_val
