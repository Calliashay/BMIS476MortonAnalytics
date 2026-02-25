import pandas as pd

def load_dataset(file_path):
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

if __name__ == "__main__":
    file_name = "AIS_2024Updated (1).csv"
    
    # Load dataset
    df = load_dataset(file_name)

    if df is not None:
        # Take random 50,000 row sample
        sample = df.sample(n=50000, random_state=42)
        
        # Save sample
        sample.to_csv("ais_sample_50k.csv", index=False)
        
        print("\nRandom 50,000 row sample saved as 'ais_sample_50k.csv'")