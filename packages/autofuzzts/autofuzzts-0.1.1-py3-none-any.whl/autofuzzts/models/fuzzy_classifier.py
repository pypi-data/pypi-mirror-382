import xgboost as xgb
from typing import Literal
from tpot import TPOTClassifier
from autofuzzts.models.mlp_nas import build_model
from sklearn.calibration import CalibratedClassifierCV


class FuzzyPipelineModel:
    def __init__(self, n_clusters: int, number_of_lags: int, verbosity: bool = False):
        self.n_clusters = n_clusters
        self.number_of_lags = number_of_lags
        self.verbosity = verbosity
        self.model = None  # Placeholder for the fitted model

    def fit(self, X_train, y_train, model_type:Literal['xgb', 'tpot','mlp']='xgb', **kwargs):
        """
        Fit the model based on the specified model type and input parameters.

        Parameters:
        - X_train: Features for training.
        - y_train: Labels for training.
        - model_type: 'xgboost', 'mlp', or 'tpot'.
        - kwargs: Additional parameters for model fitting.
        """
        if model_type == 'xgb':
            model = xgb.XGBClassifier(objective="multi:softmax", num_class=self.n_clusters, **kwargs)
            self.model = model.fit(X_train, y_train)

        elif model_type == 'tpot':
            tpot = TPOTClassifier(
                generations=kwargs.get('generations', 5),
                population_size=kwargs.get('population_size', 10),
                random_state=kwargs.get('random_state', 42),
                max_time_mins=kwargs.get('max_time_mins', 2),
            )
            tpot.fit(X_train, y_train)
            self.model = tpot.fitted_pipeline_

        elif model_type == 'mlp':
            mlp = build_model(X_train, y_train, **kwargs)  # Adjust as necessary
            self.model = mlp.fit(X_train, y_train)

        else:
            raise ValueError("Invalid model type. Choose 'xgb', 'mlp', or 'tpot'.")

        return self.model

    def calibrate(self, X_train, y_train, method='sigmoid', cv=5):
        """
        Calibrate the fitted model using CalibratedClassifierCV.

        Parameters:
        - X_train: Features for training (for calibration).
        - y_train: Labels for training (for calibration).
        - method: Calibration method ('sigmoid' or 'isotonic').
        - cv: Cross-validation splitting strategy.
        """
        if self.model is None:
            raise ValueError("Model is not fitted yet. Call 'fit' first.")

        # Ensure the model supports predict_proba
        if not hasattr(self.model, "predict_proba"):
            raise AttributeError("The fitted model does not support predict_proba.")

        # Initialize calibrated model
        calibrated_model = CalibratedClassifierCV(self.model, method=method, cv=cv)
        calibrated_model.fit(X_train, y_train)

        # Replace the model with the calibrated model
        self.model = calibrated_model

        return self.model
    def predict(self, X_test):
        """Make predictions using the fitted model."""
        if self.model is None:
            raise ValueError("Model is not fitted yet. Call 'fit_model' first.")
        return self.model.predict(X_test)
    
    def predict_proba(self, X_test):
        """Make predictions using the fitted model."""
        if self.model is None:
            raise ValueError("Model is not fitted yet. Call 'fit_model' first.")
        return self.model.predict_proba(X_test)