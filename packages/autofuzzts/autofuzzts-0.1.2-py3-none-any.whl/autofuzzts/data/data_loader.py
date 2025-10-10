import os
import pandas as pd

def load_sample_data(file_name):
    data_path = os.path.join(os.path.dirname(__file__), 'sample_datasets', file_name)
    print(f"Loading data from: {data_path}")  # Print the constructed path
    return pd.read_csv(data_path)
