import pandas as pd

REQUIRED_KEY = "Data Import Now"

def load_dataset(file_path, key):
    if key != REQUIRED_KEY:
        print("Access denied. Invalid key.")
        return None

    try:
        df = pd.read_csv(file_path)
        print("Dataset loaded successfully!\n")
        print("First 3 rows:")
        print(df.head(3))
        return df
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
