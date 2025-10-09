# config.py

DEFAULT_CONFIG = {
    "n_clusters": 3,
    "number_of_lags": 5,
    "plot_partition": False,
    "pred_column": "Y",
    "fuzzy_part_func": "triangle",
    "n_rows": 0,
    "sigma": 1.0,
    "verbosity": False,
}

def get_config(custom_config=None):
    config = DEFAULT_CONFIG.copy()
    if custom_config:
        config.update(custom_config)
    return config