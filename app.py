from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import os

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Create the FastAPI app
app = FastAPI(title="Disaster Relief AI", description="AI for Resource Allocation Command Center")

# Allow your frontend dashboard to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")

# 1. Map the file paths to your new 'model' folder
MODEL_DIR = "model"
print("Loading AI Model and preprocessing tools from /model folder...")
try:
    ai_model = joblib.load(os.path.join(MODEL_DIR, 'gradient_boosting_disaster_model.pkl'))
    num_imputer = joblib.load(os.path.join(MODEL_DIR, 'num_imputer.pkl'))
    cat_imputer = joblib.load(os.path.join(MODEL_DIR, 'cat_imputer.pkl'))
    label_encoders = joblib.load(os.path.join(MODEL_DIR, 'label_encoders.pkl'))
    print("Backend API is ready!")
except FileNotFoundError as e:
    print(f"Error loading models: {e}")
    print("Make sure your .pkl files are exactly inside the 'model' folder.")

# 2. Re-create the feature engineering function
def feature_engineering(df):
    df['logistical_urgency'] = df['nearest_relief_center_distance_km'] * (1 + df['infrastructure_damage_score'] / 100)
    df['food_deficit'] = df['requested_food_kg'] - df['food_stock_kg']
    df['water_deficit'] = df['requested_water_liters'] - df['water_stock_liters']
    df['casualty_ratio'] = (df['injuries_reported'] + df['fatalities_reported']) / (df['population_affected'] + 1)
    return df

# 3. Create a Home Route serving the UI
@app.get("/")
def home():
    return FileResponse("index.html")


# 4. Create the Prediction Endpoint
@app.post("/predict_priority")
def predict(incoming_data: dict):
    try:
        # Convert incoming JSON dictionary into a DataFrame
        df = pd.DataFrame([incoming_data])
        
        # Ensure all numerical columns expected during fit exist
        num_cols = list(num_imputer.feature_names_in_)
        for col in num_cols:
            if col not in df.columns:
                df[col] = None
                
        # Ensure all categorical columns expected during fit exist
        cat_cols = list(cat_imputer.feature_names_in_)
        for col in cat_cols:
            if col not in df.columns:
                df[col] = None
        
        # Impute missing values
        df[num_cols] = num_imputer.transform(df[num_cols])
        df[cat_cols] = cat_imputer.transform(df[cat_cols])
            
        # Encode categories
        for col in cat_cols:
            if col in label_encoders:
                le = label_encoders[col]
                df[col] = df[col].apply(lambda x: str(x) if str(x) in le.classes_ else le.classes_[0])
                df[col] = le.transform(df[col].astype(str))
                
        # Apply feature engineering
        df = feature_engineering(df)
        
        # Ensure column order matches trained model expectation
        df = df[ai_model.feature_names_in_]
        
        # Make the prediction
        prediction = ai_model.predict(df)
        priority = str(prediction[0])
        
        # Send the result back to the frontend
        return {
            'status': 'success',
            'predicted_priority': priority
        }


    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)