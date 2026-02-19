import pandas as pd

def load_dataset(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Dataset loaded successfully!\n")
        print("First 3 rows:")
        print(df.head())
        return df
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_name = "AIS_2024_01_01.csv"  # <-- 
    data = load_dataset(file_name)