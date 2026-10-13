import pandas as pd
import joblib
import os
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

def preprocess_and_save(input_csv_path, output_dir="."):
    print(f"Loading raw dataset from {input_csv_path}...")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: The file {input_csv_path} was not found.")
        return

    # 1. Separate features (X) and target (y)
    # Also drop columns that won't be used for training
    target_col = 'allocation_priority'
    cols_to_drop = [
        'request_id', 
        'timestamp_reported', 
        'field_notes', 
        'recommended_relief_units',
        target_col
    ]
    
    y = df[target_col]
    X = df.drop(columns=cols_to_drop)

    print("Identifying column types...")
    cat_cols = X.select_dtypes(include=['object', 'bool']).columns.tolist()
    num_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

    # 2. Impute missing values
    print("Imputing missing values...")
    # For numbers: use median to be robust against extreme outliers
    num_imputer = SimpleImputer(strategy='median')
    X[num_cols] = num_imputer.fit_transform(X[num_cols])

    # For categories: use the most frequent value (mode)
    cat_imputer = SimpleImputer(strategy='most_frequent')
    X[cat_cols] = cat_imputer.fit_transform(X[cat_cols])

    # 3. Encode categorical variables
    print("Encoding categorical variables...")
    label_encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        # Convert to string to ensure consistent encoding, especially for booleans
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

    # 4. Save the preprocessing objects (Crucial for the Hackathon Backend API)
    print("Saving imputers and encoders for live predictions...")
    joblib.dump(num_imputer, os.path.join(output_dir, 'num_imputer.pkl'))
    joblib.dump(cat_imputer, os.path.join(output_dir, 'cat_imputer.pkl'))
    joblib.dump(label_encoders, os.path.join(output_dir, 'label_encoders.pkl'))

    # 5. Save the cleaned datasets
    print("Saving preprocessed datasets...")
    # Re-attach the target column to save a unified cleaned dataset
    df_cleaned = X.copy()
    df_cleaned[target_col] = y.values
    
    cleaned_csv_path = os.path.join(output_dir, 'cleaned_disaster_data.csv')
    df_cleaned.to_csv(cleaned_csv_path, index=False)
    
    print(f"Success! Cleaned data saved to '{cleaned_csv_path}'.")
    print("Preprocessing objects saved as .pkl files.")

if __name__ == "__main__":
    # Define your input file
    RAW_DATA_FILE = 'disaster_relief_resource_allocation.csv'
    
    # Run the pipeline
    preprocess_and_save(RAW_DATA_FILE)