# pipeline.py
import pandas as pd
from typing import Dict, Literal
import optuna
import numpy as np

from autofuzzts.config import get_config
from autofuzzts.data import data_loader
from autofuzzts.data_validation.validate import validate_and_clean_input
from autofuzzts.partition.partition import FuzzyPartition
from autofuzzts.preprocess.preprocess import preprocess_data,preprocess_data_val
from autofuzzts.preprocess.prep_for_model import prepare_for_model,prepare_for_model_val_set
from autofuzzts.models.fuzzy_classifier import FuzzyPipelineModel

from sklearn.model_selection import ParameterGrid
from sklearn.calibration import CalibratedClassifierCV


## Import RMSE and MAE
from sklearn.metrics import root_mean_squared_error, mean_absolute_error,mean_squared_error

# Example custom configuration
custom_config = {
    "n_clusters": 5,
    "verbosity": True,
}

# Retrieve the final configuration
selected_config = get_config(custom_config)



def run_pipeline(datasetet_name: str, config: dict = selected_config):
    # Load data

    data = data_loader.load_sample_data(datasetet_name)
    print(data.head(5))
    print('Evaluated configuration is')
    print(config)

    pass
  

def train_val_pipeline(train_set:pd.DataFrame,val_set:pd.DataFrame,config:Dict = selected_config, metric:Literal['rmse','mse','mae'] = 'rmse', 
                       diff_type:Literal['perc','abs'] = 'perc', covariates:list[str] = None) -> float:
    train_set = validate_and_clean_input(train_set, covariates)
    val_set = validate_and_clean_input(val_set, covariates)

    print('train set length:', len(train_set))

    if covariates :
        train_covariates = train_set[covariates].copy()
        val_covariates = val_set[covariates].copy() 


    train_set_preprocessed, scaler_train = preprocess_data(train_set, diff_type)
    val_set_preprocessed = preprocess_data_val(df=val_set, df_train=train_set, diff_type=diff_type, scaler=scaler_train)

       
    fp = FuzzyPartition(fuzzy_function=config['fuzzy_part_func'], n_clusters=config['n_clusters'], sigma=config['sigma'], scaler=scaler_train, verbosity=config['verbosity'])

    # Prepare train and validation fuzzy partitions
    X_training = train_set_preprocessed['diff_scaled'].values
    X_validation = val_set_preprocessed['diff_scaled'].values


    train_fuzzy_partition,_,_  = fp.fuzzy_partition(X_training)
    val_fuzzy_partition, _,center_points_unscaled_test_val  = fp.fuzzy_partition(X_validation)

    X_train, y_train = prepare_for_model(train_fuzzy_partition.copy(), config['number_of_lags'])
    X_val, y_val = prepare_for_model_val_set(df_val_fp = val_fuzzy_partition.copy(),df_train_fp = train_fuzzy_partition.copy(),n_lags = config['number_of_lags'])

       
    if covariates:
        X_train = pd.concat([X_train, train_covariates], axis=1)
        X_val = pd.concat([X_val, val_covariates], axis=1)

    model = FuzzyPipelineModel(n_clusters=config['n_clusters'], number_of_lags=config['number_of_lags'], verbosity=config['verbosity'])


    model.fit(X_train, y_train, model_type='xgb')

    pred_cluster = model.predict(X_val)


    ## Convert prediction to crips number using center points of clusters
    y_val_pred_center_point = [center_points_unscaled_test_val[i] for i in pred_cluster]




    ## Recalculate percentage difference to actual values
    y_val_pred= [None] * len(val_set)

    # Set the first prediction using the last known value from the train set
    last_train_value = train_set['Y'].iloc[-1]  # Assuming `df_train` holds the training data
    y_val_pred[0] = last_train_value * (1 + y_val_pred_center_point[0])

    # Loop to calculate each subsequent prediction based on the actual previous value in `df_test['Y']`

    if diff_type == 'perc':
        for i in range(1, len(val_set)):
            prev_Y = val_set['Y'].iloc[i-1]  # Use the previous actual value from `df_test`
            perc_change = y_val_pred_center_point[i]
            y_val_pred[i] = prev_Y * (1 + perc_change)

    elif diff_type == 'abs':
        for i in range(1, len(val_set)):
            prev_Y = val_set['Y'].iloc[i-1]
            y_val_pred[i] = prev_Y + y_val_pred_center_point[i]
        

    if metric == 'rmse':
        metric_value = root_mean_squared_error(val_set['Y'], y_val_pred)
    elif metric == 'mse':
        metric_value = root_mean_squared_error(val_set['Y'], y_val_pred)**2
    elif metric == 'mae':
        metric_value = mean_absolute_error(val_set['Y'], y_val_pred)
    else:
        raise ValueError(f"Invalid metric {metric}. Please choose one of 'rmse', 'mse', 'mae'")
  
    return metric_value

def train_model(dataset: pd.DataFrame, config: Dict, model_type: Literal['xgb','mlp','tpot'] = 'xgb'):
    '''
    Function to train a model on the dataset provided.

    Parameters:
    dataset: pd.DataFrame
        The dataset to train the model on.
    config: dict
        The configuration dictionary for the model.
    model_type: str
        The type of model to train. Default is 'xgb'.
    
    '''
    config = get_config(config)

    df = validate_and_clean_input(dataset)
    
    df_preprocessed, scaler_train = preprocess_data(df, diff_type='perc')

       
    fp = FuzzyPartition(fuzzy_function=config['fuzzy_part_func'], n_clusters=config['n_clusters'], sigma=config['sigma'], scaler=scaler_train, verbosity=config['verbosity'])

    X_training = df_preprocessed['diff_scaled'].values

    train_fuzzy_partition,_,_  = fp.fuzzy_partition(X_training)

    X_train, y_train = prepare_for_model(train_fuzzy_partition.copy(), config['number_of_lags'])

    model_train = FuzzyPipelineModel(n_clusters=config['n_clusters'], number_of_lags=config['number_of_lags'], verbosity=config['verbosity'])

    model_train.fit(X_train, y_train, model_type=model_type)
  
    
    return model_train, scaler_train

def tune_hyperparameters_bayes(train_set: pd.DataFrame, val_set: pd.DataFrame, n_trials: int = 315, metric: Literal['rmse', 'mse', 'mae'] = 'rmse', 
                               diff_type: Literal['perc', 'abs'] = 'perc', covariates: list[str] = None):
    def objective(trial):
        # Define search space based on your specifications
        config = {
            'n_clusters': trial.suggest_int('n_clusters', 4, 40),  # Number of fuzzy sets
            'number_of_lags': trial.suggest_int('number_of_lags', 1, 10),  # Number of lags
            'fuzzy_part_func': trial.suggest_categorical('fuzzy_part_func', ['Triangle', 'Cosine', 'Gaussian']),  # Partition function type
        }

        if config['fuzzy_part_func'] == 'Gaussian':
            config['sigma'] = trial.suggest_float('sigma', 0.1, 4, log=True)
        else:
            config['sigma'] = None

        selected_config = get_config(config)

        # Use train_val_pipeline to evaluate this configuration
        metric_value = train_val_pipeline(train_set, val_set, selected_config, metric, diff_type, covariates=covariates)
        return metric_value


    # Create and optimize the Optuna study
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    # Extract the best configuration and score
    best_config = study.best_params
    best_metric_value = study.best_value

    print(f"Best Config: {best_config}")
    print(f"Best {metric.upper()}: {best_metric_value}")
    return best_config, best_metric_value


def tune_hyperparameters_bayes_Henon(train_set: pd.DataFrame, val_set: pd.DataFrame, n_trials: int = 315, metric: Literal['rmse', 'mse', 'mae'] = 'rmse', diff_type: Literal['perc', 'abs'] = 'perc'):
    def objective(trial):
        config = {
        'n_clusters': trial.suggest_int('n_clusters', 2, 29),  # Number of fuzzy sets
        'number_of_lags': trial.suggest_int('n_lags', 2, 5),  # Number of lags
        'fuzzy_part_func': trial.suggest_categorical('fuzzy_part_func', ['Triangle', 'Cosine', 'Gaussian']),
        }

        if config['fuzzy_part_func'] == 'Gaussian':
            config['sigma'] = trial.suggest_float('sigma', 0.1, 4, log=True)
        else:
            config['sigma'] = None
        
        selected_config = get_config(config)

        # Use train_val_pipeline to evaluate this configuration
        metric_value = train_val_pipeline(train_set, val_set, selected_config, metric,diff_type)
        return metric_value


    # Create and optimize the Optuna study
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    # Extract the best configuration and score
    best_config = study.best_params
    best_metric_value = study.best_value

    print(f"Best Config: {best_config}")
    print(f"Best {metric.upper()}: {best_metric_value}")
    return best_config, best_metric_value





def tune_hyperparameters_grid(train_set: pd.DataFrame, val_set: pd.DataFrame,n_trials: int = 315, metric: Literal['rmse', 'mse', 'mae'] = 'rmse', diff_type: Literal['perc', 'abs'] = 'perc'):
    
    # Define grid for Gaussian fuzzy function (includes 'sigma')
    grid_gauss = {
        'n_lags': [1, 3, 5, 7, 9],
        'n_clusters': [4, 6, 8, 10, 12, 14, 16, 18, 20],
        'sigma': [0.1, 0.5, 1, 5, 9],
        'fuzzy_part_func': ['matrix_F_transform_gauss']
    }

    # Define grid for non-Gaussian fuzzy functions (excludes 'sigma')
    grid_non_gauss = {
        'n_lags': [1, 3, 5, 7, 9],
        'n_clusters': [4, 6, 8, 10, 12, 14, 16, 18, 20],
        'sigma': [None],  # Set sigma to None for non-Gaussian functions
        'fuzzy_part_func': ['matrix_F_transform_cosine', 'matrix_F_transform_triangle']
    }

    # Combine the grids
    grid_gauss = list(ParameterGrid(grid_gauss))
    grid_non_gauss = list(ParameterGrid(grid_non_gauss))
    combined_grid = grid_gauss + grid_non_gauss

    ## Run the grid search------------------------------------------------------------------------------------------------------
    best_metric_value = float("inf")
    best_config = None
    num_evaluations = 0

    for config in combined_grid:
        selected_config = get_config(config)
        # Count the configuration being evaluated
        num_evaluations += 1

        if num_evaluations >= n_trials:
            break

        ## If number of evaluation is divisible by 20 print the number of evaluations
        if num_evaluations % 20 == 0:
            print(f"Number of evaluations done: {num_evaluations}")

        # Evaluate the config on the validation set using train_val_pipeline
        metric_value = train_val_pipeline(train_set, val_set, selected_config, metric, diff_type)

        # Update best config if this one is better according to the selected metric
        if metric_value < best_metric_value:
            best_metric_value = metric_value
            best_config = config


    return best_config, best_metric_value, num_evaluations




def train_calib_pred_test(train_set: pd.DataFrame, test_set: pd.DataFrame, 
                     config: Dict,
                     model_type: Literal['xgb','mlp','tpot'] = 'xgb', number_cv_calib = 5, diff_type: Literal['perc','abs'] = 'perc',
                     covariates: list[str] = None, exclude_bool:bool = False) -> float:
    '''
    Aim of this question is to train a model on the train set, calibrate it using the calibration method provided, and predict it on the test set using the metric provided.
    '''

    config = get_config(config)
    
    # Step 1: Validate and preprocess the input data
    train_set = validate_and_clean_input(train_set, covariates=covariates)
    test_set = validate_and_clean_input(test_set, covariates=covariates)

    train_set_preprocessed, scaler_train = preprocess_data(train_set, diff_type=diff_type)
    test_set_preprocessed = preprocess_data_val(df=test_set, df_train=train_set, diff_type=diff_type, scaler=scaler_train)

    # Step 2: Fuzzy Partition for train, validation, and test sets
    fp = FuzzyPartition(fuzzy_function=config['fuzzy_part_func'], 
                        n_clusters=config['n_clusters'], 
                        sigma=config['sigma'], 
                        scaler=scaler_train, 
                        verbosity=config['verbosity'])

    # Prepare train, validation, and test fuzzy partitions
    X_training = train_set_preprocessed['diff_scaled'].values
    X_test = test_set_preprocessed['diff_scaled'].values

    train_fuzzy_partition, _, _ = fp.fuzzy_partition(X_training)
    test_fuzzy_partition, _, center_points_unscaled_test = fp.fuzzy_partition(X_test)

    if exclude_bool:
        ## Remove column left from train_fuzzy_partition
        train_fuzzy_partition = train_fuzzy_partition.drop(columns=['left'])
        test_fuzzy_partition = test_fuzzy_partition.drop(columns=['left'])

    train_fuzzy_partition.to_csv('train_fuzzy_partition.csv')
    test_fuzzy_partition.to_csv('test_fuzzy_partition.csv')

    print('center_points_unscaled_test:', center_points_unscaled_test)

    # Prepare data for model training, validation, and testing
    X_train, y_train = prepare_for_model(train_fuzzy_partition.copy(), config['number_of_lags'])
    X_test_final, _ = prepare_for_model_val_set(df_val_fp=test_fuzzy_partition.copy(),
                                                           df_train_fp=train_fuzzy_partition.copy(),
                                                           n_lags=config['number_of_lags'])
    
    if covariates:
        train_covariates = train_set[covariates].copy()
        test_covariates = test_set[covariates].copy() 

        X_train = pd.concat([X_train, train_covariates], axis=1)
        X_test_final = pd.concat([X_test_final, test_covariates], axis=1)
    

    # Step 3: Train the model on the combined train and validation set
    model = FuzzyPipelineModel(n_clusters=config['n_clusters'], 
                               number_of_lags=config['number_of_lags'], 
                               verbosity=config['verbosity'])
 
    model.fit(X_train, y_train, model_type=model_type)

    try:
        # Step 4: Calibrate the model using CalibratedClassifierCV
        model.calibrate(X_train, y_train, method='sigmoid', cv=number_cv_calib)
    except:
        pass

    # Step 5: Make predictions and evaluate on the test set
    y_test_pred_cluster = model.predict(X_test_final)

    ## Convert prediction to crips number using center points of clusters
    y_test_pred_center_point = [center_points_unscaled_test[i] for i in y_test_pred_cluster]




    ## Recalculate percentage difference to actual values
    y_test_pred= [None] * len(test_set)

    # Set the first prediction using the last known value from the train set
    last_train_value = train_set['Y'].iloc[-1]  # Assuming `df_train` holds the training data
    y_test_pred[0] = last_train_value * (1 + y_test_pred_center_point[0])

    if diff_type == 'perc':
        # Loop to calculate each subsequent prediction based on the actual previous value in `df_test['Y']`
        for i in range(1, len(test_set)):
            prev_Y = test_set['Y'].iloc[i-1]  # Use the previous actual value from `df_test`
            perc_change = y_test_pred_center_point[i]
            y_test_pred[i] = prev_Y * (1 + perc_change)

    elif diff_type == 'abs':
        for i in range(1, len(test_set)):
            prev_Y = test_set['Y'].iloc[i-1]
            y_test_pred[i] = prev_Y + y_test_pred_center_point[i]

    return y_test_pred_cluster, y_test_pred_center_point,y_test_pred



