import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
import joblib
import matplotlib.pyplot as plt

def feature_engineering(df):
    print("Engineering novel features...")
    # 1. Logistical Urgency: High damage and long distance means harder to reach
    df['logistical_urgency'] = df['nearest_relief_center_distance_km'] * (1 + df['infrastructure_damage_score'] / 100)
    
    # 2. Resource Deficits: How short are they on survival items?
    df['food_deficit'] = df['requested_food_kg'] - df['food_stock_kg']
    df['water_deficit'] = df['requested_water_liters'] - df['water_stock_liters']
    
    # 3. Impact Severity: Ratio of casualties to affected population
    # Adding 1 to denominator to avoid division by zero
    df['casualty_ratio'] = (df['injuries_reported'] + df['fatalities_reported']) / (df['population_affected'] + 1)
    
    return df

def train_advanced_model(csv_path):
    print(f"Loading cleaned dataset from '{csv_path}'...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find '{csv_path}'.")
        return

    # Apply Feature Engineering
    df = feature_engineering(df)

    # Define Features (X) and Target (y)
    target_col = 'allocation_priority'
    y = df[target_col]
    X = df.drop(columns=[target_col])

    # Train-Test Split
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train HistGradientBoosting Classifier (The native XGBoost alternative)
    print("Training HistGradientBoosting Classifier (Optimized for Accuracy)...")
    hgb = HistGradientBoostingClassifier(
        max_iter=300,
        learning_rate=0.05,
        max_depth=8,
        random_state=42
    )
    
    hgb.fit(X_train, y_train)

    # Evaluate the Model
    print("\n--- Advanced Model Evaluation ---")
    y_pred = hgb.predict(X_test)
    print(f"Overall Gradient Boosting Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
    print(classification_report(y_test, y_pred))

    # Save the Model
    joblib.dump(hgb, 'gradient_boosting_disaster_model.pkl')
    print("Advanced model saved as 'gradient_boosting_disaster_model.pkl'")

    # --- THE NOVELTY: EXPLAINABLE AI ---
    print("\nGenerating AI Explanation (Permutation Importance)...")
    
    # Calculate feature importance
    result = permutation_importance(
        hgb, X_test, y_test, n_repeats=5, random_state=42, n_jobs=-1
    )
    
    # Get the top 10 most important features
    sorted_idx = result.importances_mean.argsort()[-10:]
    
    # Plot the results
    plt.figure(figsize=(12, 6))
    
    # Generate the boxplot without the 'labels' argument to prevent version errors
    plt.boxplot(
        result.importances[sorted_idx].T,
        vert=False
    )
    
    # Safely apply labels using yticks instead
    plt.yticks(ticks=range(1, 11), labels=X_test.columns[sorted_idx])
    
    plt.title("Explainable AI: Top 10 Decision Drivers for Resource Allocation")
    plt.xlabel("Impact on Accuracy (How much the AI relies on this data)")
    plt.tight_layout()
    
    # Save the chart
    plt.savefig('ai_explanation_novelty.png')
    print("Saved 'ai_explanation_novelty.png'. Show this in your PPT!")

if __name__ == "__main__":
    train_advanced_model('cleaned_disaster_data.csv')