from sklearn.neural_network import MLPClassifier  # Assuming you use sklearn's MLP
from sklearn.model_selection import train_test_split
import optuna


def _objective(trial, X, y):
    """
    This is the objective function used for hyperparameter tuning
    (internal function).
    """
    # ... Same code as before inside objective function ...

    # Split data
    x_train, x_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Define and train the model with suggested hyperparameters
    clf = MLPClassifier(
        hidden_layer_sizes=tuple(
            trial.suggest_int(f"n_units_{i}", 10, 100)
            for i in range(trial.suggest_int("n_layers", 1, 4))
        ),
        activation=trial.suggest_categorical("activation", ["relu", "tanh"]),
        solver="adam",  # Using only 'adam' solver
        alpha=trial.suggest_float("alpha", 1e-5, 1e-1, log=True),
        learning_rate_init=trial.suggest_float("learning_rate_init", 1e-4, 1e-2, log=True),
        max_iter=200,
        random_state=42,
        early_stopping=True,
        n_iter_no_change=10,
    )
    clf.fit(x_train, y_train)

    # Evaluate the model
    return clf.score(x_test, y_test)

def build_model(X, y, n_trials=100):
    """
    This function performs hyperparameter tuning, builds, trains, and
    returns a fitted MLP classifier model.

    Args:
        X: Training data features.
        y: Training data labels.
        n_trials: Number of trials for hyperparameter tuning (default: 100).

    Returns:
        A fitted MLPClassifier model.
    """
    # Define the neural network structure search space
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: _objective(trial, X, y), n_trials=n_trials)

    # Print best parameters and best score
    print(f"Best parameters: {study.best_params}")
    print(f"Best score: {study.best_value}")

    # Extract best hyperparameters
    n_layers = study.best_params["n_layers"]
    hidden_layer_sizes = tuple(
        [study.best_params[f"n_units_{i}"] for i in range(n_layers)]
    )
    activation = study.best_params["activation"]
    alpha = study.best_params["alpha"]
    learning_rate_init = study.best_params["learning_rate_init"]

    # Print model architecture
    print("Model Architecture:")
    print(f"\tNumber of Layers: {n_layers}")
    print(f"\tHidden Layer Sizes: {hidden_layer_sizes}")
    print(f"\tActivation Function: {activation}")
    print(f"\tL2 Penalty (alpha): {alpha}")
    print(f"\tInitial Learning Rate: {learning_rate_init}")

    # Create the model with best hyperparameters
    model = MLPClassifier(
        hidden_layer_sizes=hidden_layer_sizes,
        activation=activation,
        solver="adam",
        alpha=alpha,
        learning_rate_init=learning_rate_init,
        max_iter=200,
        random_state=42,
        early_stopping=True,
        n_iter_no_change=10,
    )

    return model

