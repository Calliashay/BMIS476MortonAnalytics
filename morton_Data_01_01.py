import pandas as pd

def load_dataset(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Dataset loaded successfully!\n")
        print("First 5 rows:")
        print(df.head())
        return df
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_name = "AIS_2024_01_01"  # <-- Replace this
    data = load_dataset(file_name)
