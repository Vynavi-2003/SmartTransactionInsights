import pandas as pd

def load_and_clean_data(file_path):
    try:
        df = pd.read_csv(file_path)

        # Standardize column names
        df.columns = df.columns.str.strip().str.lower()

        # Drop completely empty rows
        df.dropna(how='all', inplace=True)

        # Remove duplicate rows
        df.drop_duplicates(inplace=True)

        # Handle missing values
        if df.isnull().sum().sum() > 0:
            print("[INFO] Missing values found. Filling with 'Unknown' or 0.")
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col].fillna("Unknown", inplace=True)
                else:
                    df[col].fillna(0, inplace=True)

        # Parse date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df.dropna(subset=['date'], inplace=True)
        else:
            raise ValueError("Missing 'date' column.")

        # Add derived time columns
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year

        # Cast numeric columns
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

        return df

    except Exception as e:
        print(f"[ERROR] Failed to load or clean data: {e}")
        return pd.DataFrame()
