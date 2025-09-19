# predict_ml.py
# This script loads a trained ML model and predicts the priority of a new description.

import sys
import joblib

# --- Configuration ---
VECTORIZER_FILE = "vectorizer.joblib"
MODEL_FILE = "model.joblib"

def predict_priority(description):
    """Loads the model and predicts the priority of a given description."""
    try:
        # 1. Load the vectorizer and model
        vectorizer = joblib.load(VECTORIZER_FILE)
        model = joblib.load(MODEL_FILE)
    except FileNotFoundError:
        print("Error: Model or vectorizer files not found.")
        print("Please run `model_training_ml.py` first to train and save the model.")
        return None

    # 2. Transform the new description using the loaded vectorizer
    description_tfidf = vectorizer.transform([description])

    # 3. Predict the priority
    prediction = model.predict(description_tfidf)
    prediction_proba = model.predict_proba(description_tfidf)
    
    # Get the confidence score for the predicted class
    confidence = max(prediction_proba[0])
    
    return {
        "priority": prediction[0],
        "confidence": confidence
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_description = " ".join(sys.argv[1:])
    else:
        print("Usage: python predict_ml.py \"<your issue description>\"")
        print("Example: python predict_ml.py \"a huge fire is starting near the main highway\"")
        sys.exit(1)

    print(f"\nAnalyzing with ML model: \"{input_description}\"")
    
    result = predict_priority(input_description)
    
    if result:
        print("\n--- ML Prediction Result ---")
        print(f"Predicted Priority: {result['priority']}")
        print(f"Confidence Score:   {result['confidence']:.2%}")
        print("--------------------------\n")
